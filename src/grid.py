from tkinter import *
from tkinter.ttk import *
from const import *
from vertex import *
from pqueue import *
from tkWindowInput import tk_window_input
import numpy as np
from filtration_fnc import inner_mat_prod, pred_form_stateEstimMat
from chooseNeighbourVer import *


class Grid:

    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("A* Visualizer")

        self.grid:list[list[Vertex]] = [None for _ in range(NUM_ROW)]
        for i in range(NUM_ROW):
            self.grid[i] = [None for _ in range(NUM_COL)]

        for i in range(NUM_ROW):
            for j in range(NUM_COL):
                self.grid[i][j] = Vertex(i , j)

        Vertex.win = self.win
        self.draw_all()

        self.running: bool = True
        self.mode = Mode.OBSTACLE
        self.hold: bool = False           # Obsticle mode
        self.invasive = None
        self.start_ver: Vertex = None
        self.s_ver: Vertex = None
        self.e_ver: Vertex = None
        self.s_chosen = self.e_chosen = False
        self.front = PriorityQueue()
        self.transitionMat: np.ndarray = tk_window_input('Input transition matrix')
        self.transitionMat = self.transitionMat/self.transitionMat.sum()
        self.emissionMat: np.ndarray = tk_window_input('Input emission matrix')
        self.emissionMat = self.emissionMat/self.emissionMat.sum()
        self.rotatedEmissionMat: np.ndarray = np.rot90(self.emissionMat, 2)
        self.realPosition: Vertex = None
        self.emissionReading: Vertex = None
        self.desiredStep: Vertex = None
        self.stateEstimMat: np.ndarray = np.zeros((3, 3)) # centered is emissionReading
        self.stateEstimMat[1][1] = 1
        self.stateEstimMatCenter: Vertex = None


 

    def is_running(self):
        return self.running

    def get_ver_pos(self):
        pos = pygame.mouse.get_pos()
        return self.grid[pos[0]//VER_WIDTH][pos[1]//VER_HEIGHT]

    def on_done(self):
        self.mode = Mode.PATH
        self.invasive.destroy()

    def on_resume(self):
        self.invasive.destroy()
    
    def on_rerun(self):
        self.invasive.destroy()
        self.__init__()

    def on_exit(self):
        self.running = False
        self.invasive.destroy()

    def draw_all(self):
        self.win.fill(BLACK)
        for i in range(NUM_ROW):
            for j in range(NUM_COL):
                self.grid[i][j].display()

    def decide(self):
        if self.mode == Mode.OBSTACLE:
            self.obstacle_handle()
            
        elif self.mode == Mode.PATH:
            self.path_handle()

        elif self.mode == Mode.PRE_SIM:
            self.pre_sim_handle()

        elif self.mode == Mode.SIMULATION:
            self.simulation_handle()

        elif self.mode == Mode.RECONSTRUCT:
            self.reconstruct_handle()
        
        elif self.mode == Mode.MAKE_STEP:
            self.make_step_handle()   

    def obstacle_handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif self.hold and self.mode == Mode.OBSTACLE:
                if event.type == pygame.MOUSEBUTTONUP:
                    self.get_ver_pos().set_obstacle(True) 
                    self.hold = False
                else:
                    self.get_ver_pos().set_obstacle(True) 
            elif not self.hold and event.type == pygame.MOUSEBUTTONDOWN:
                if self.mode == Mode.OBSTACLE:
                    self.get_ver_pos().set_obstacle(True)
                    self.hold = True
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.invasive = Tk()
                self.invasive.geometry('205x110+850+490')
                frame = Frame(self.invasive)

                Label(frame, 
                    text = '\nAre you done putting up obstacles\n           and want to proceed?\n').pack(side = 'top')
                Button(frame, width=12, text = 'Resume',
                    command=lambda : self.on_resume()).pack(side = 'left')
                Button(frame, width=12, text = 'Done!',
                    command=lambda : self.on_done()).pack(side = 'right')

                frame.pack()
                self.invasive.title('Obstacles')
                self.invasive.mainloop()

    def path_handle(self):
        firstIter = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.s_chosen and self.e_chosen:
                self.mode = Mode.PRE_SIM
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.s_chosen:
                    self.s_ver = self.get_ver_pos()
                    self.s_ver.set_point(True)
                    self.start_ver = self.s_ver
                    self.start_ver.color = Vertex.START_POS
                    self.start_ver.display()
                    self.emissionReading = self.s_ver
                    self.s_chosen = True
                    if firstIter == True:
                        self.stateEstimMatCenter = self.s_ver
                        firstIter = False
                elif not self.e_chosen:
                    self.e_ver = self.get_ver_pos()
                    if self.s_ver == self.e_ver:
                        continue
                    self.e_ver.set_point(True)
                    self.e_ver.color = Vertex.END_POS
                    self.e_ver.display()
                    self.e_chosen = True

    def pre_sim_handle(self): 
        for row in self.grid:
            for vertex in row:
                vertex.appoint_neighbours(self.grid)
                vertex.appoint_heuristic(self.e_ver)
        self.front.put(self.s_ver, 0)
        self.s_ver.came_from = None
        self.s_ver.cost_so_far = 0
        self.mode = Mode.SIMULATION
        

    def simulation_handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
        if self.front.empty():
            self.running = False
            return
        current:Vertex = self.front.get()
        if current == self.e_ver:
            self.mode = Mode.RECONSTRUCT
            current.set_visit(self.s_ver, self.e_ver)
            current.display()
            self.backtrack: Vertex = self.e_ver
            return
        for next in current.neighbours:
            new_cost = current.cost_so_far + 1
            if next.cost_so_far == -1 or new_cost < next.cost_so_far:
                next.cost_so_far = new_cost
                priority = new_cost + next.hst
                self.front.put(next, priority)
                next.came_from: Vertex = current
                next.color = Vertex.EDG_COLOR
                next.display()
        current.set_visit(self.s_ver, self.e_ver)
        current.display()


    def reconstruct_handle(self):        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
        if self.backtrack != self.s_ver:
            self.backtrack.recon()
            self.backtrack: Vertex = self.backtrack.came_from
            if self.backtrack.came_from == self.s_ver: 
                self.desiredStep = self.backtrack
        else:
            self.s_ver.display()
            self.mode = Mode.MAKE_STEP


    def make_step_handle(self):
        if self.e_ver == self.s_ver:
            self.running = False
        temp_e_ver = self.e_ver
        temp_s_ver = self.s_ver
        for i in range(NUM_ROW):
            for j in range(NUM_COL):
                ver = self.grid[i][j]
                if not ver.obs:
                    ver.color = ver.DEF_COLOR
                    ver.pnt = ver.vst = False
                    ver.neighbours = []
                    ver.cost_so_far = ver.hst = -1
                    ver.vst_ngh = 0
                    ver.came_from = None
                    ver.display()

        self.e_ver = temp_e_ver        
        self.e_ver.recon()
        self.e_ver.color = Vertex.END_POS
        self.e_ver.display()
        rotatedTransitionMat = self.transitionMat
        if self.desiredStep.x == temp_s_ver.x - 1:
           pass
        elif self.desiredStep.x == temp_s_ver.x + 1:
            rotatedTransitionMat = np.rot90(self.transitionMat, 2)
        elif self.desiredStep.y == temp_s_ver.y - 1:
            rotatedTransitionMat = np.rot90(self.transitionMat)
        elif self.desiredStep.y == temp_s_ver.y + 1:
            rotatedTransitionMat = np.rot90(self.transitionMat, -1)

        _, move_p = choose_position(rotatedTransitionMat)
        while self.grid[temp_s_ver.x + move_p[0]][temp_s_ver.y + move_p[1]].obs == True:
            _, move_p = choose_position(rotatedTransitionMat)


        self.realPosition = self.grid[temp_s_ver.x + move_p[0]][temp_s_ver.y + move_p[1]]

        _, move_e = choose_emission(self.emissionMat)

        if True:    # Start vertex == realPosition, although realPosition is stochastically chosen
            self.s_ver = self.realPosition
            self.filtrate_reading()
        else:       # Start vertex != realPosition, realPosition and emission are stochastically chosen
            pass
            # self.emissionReading = self.grid[self.realPosition.x + move_e[0]][self.realPosition.y + move_e[1]]
            # predictionMat = self.pred_form_stateEstimMat()
            # predictionMatCut = predictionMat[self.emissionReading.x-1:self.emissionReading.x+2, self.emissionReading.y-1:self.emissionReading.y+2]
            # self.s_ver = self.grid[self.realPosition.x + move_e[0]][self.realPosition.y + move_e[1]]
            # self.filtrate_reading(predictionMatCut)
 
        self.s_ver.recon()
        self.start_ver.color = Vertex.START_POS
        self.start_ver.display()
        self.display_real_pos()
        self.mode = Mode.PATH
        


    def filtrate_reading(self): # Filtration
        rotEmMatCopy = np.copy(self.rotatedEmissionMat)
        statePredictionMat = pred_form_stateEstimMat(self.s_ver, self.desiredStep, self.transitionMat, self.stateEstimMat)
        cuted_statePredictionMat = statePredictionMat[self.emissionReading.x-self.stateEstimMatCenter.x+1:self.emissionReading.x-self.stateEstimMatCenter.x+4,
                                                      self.emissionReading.y-self.stateEstimMatCenter.y+1:self.emissionReading.y-self.stateEstimMatCenter.y+4]

        self.stateEstimMat = np.multiply(rotEmMatCopy, cuted_statePredictionMat)



    def display_real_pos(self):
        self.grid[self.realPosition.x][self.realPosition.y].color = self.realPosition.REAL_POS
        self.grid[self.realPosition.x][self.realPosition.y].display()