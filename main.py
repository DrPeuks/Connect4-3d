from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *




import concurrent.futures

from engine import Connect4Engine


from primitiveMaker import createRect, createCylinder

from math import sin, cos, tan, pi

from random import randint, choice
from time import time



configvars = """
win-size 1200 600
window-title Connect 4
show-frame-rate-meter 1
task-timer-verbose #t
win-origin -2, -2
"""

loadPrcFileData("", configvars)









class Connect4(ShowBase):

    def __init__(self):

        super().__init__()


        #self.disableMouse() # use for testing and debugging





        self.eng = Connect4Engine()



        self.cameraTarget = 'left'
        self.angleDegrees = 0
        self._angleDegrees = 0 # used for comparison at line 603, to keep this angle in an acceptable range
        self.angleRadians = 0 # used for setting the camera's position, Panda3d only supports angles in radians
        self.cameraRotationType = 'fancy' # 'fancy' when the player is thinking, 'turn' for a fast rotation at each play

        self.cam_dist = 460

        self.cameraSide = 0
        self.refAngle = 0
        self.resetAngle= False




        self.coins = []
        self.currcoin = 0

        self.cols_xranges = [
            [-100, -65, 0],
            [-60, -42, 1],
            [-32, -19.5, 2],    # ranges of x coordinates for each col
            [-10, 5, 3],
            [12, 27, 4],
            [34, 51, 5 ],
            [61, 100, 6]
        ]


        self.drop_row = -1


        self.turn = 0

        self.gameOver = False
        self.isDropping = False
        self.vUp = 0
        self.stored_time = time()


        self.x_size = 13.793418884277344*1.7 # space between 2 bars


        self.aiScreen = None
        self.ai_playing = False
        self.lvl = -1
        self.setup_gui()


        self.text = None
        self.textNodePath = None
        self.rematchBtn = None






        self.light_node = PointLight("point_light")
        self.light_node.set_color((1., 1., 1., 1.))
        self.light = base.camera.attach_new_node(self.light_node)
        self.light.set_pos(5., -10., 7.)
        self.render.set_light(self.light)




        name = choice(['earth', 'mercury', 'mars', 'moon', 'phobos', 'venus'])
        self.earth = loader.loadModel("models/planet_sphere.bam")
        self.earth_tex = loader.loadTexture(f"models/{name}_1k_tex.jpg")
        self.earth.setTexture(self.earth_tex, 1)
        self.earth.setScale(300)
        self.earth.setZ(-400)
        self.earth.reparentTo(self.render)

        self.sky = loader.loadModel("models/solar_sky_sphere.bam")
        self.sky_tex = loader.loadTexture("models/stars_1k_tex.jpg")
        self.sky.setTexture(self.sky_tex, 1)
        self.sky.reparentTo(render)
        self.sky.setScale(500)





    def setup_gui(self):

        self.titleMenuBackdrop = DirectFrame(frameColor = (0, 0, 0, 1),
                                     frameSize = (-1, 1, -1, 1),
                                     parent = self.render2d)


        self.titleMenu = DirectFrame(frameColor = (1, 1, 1, 0))


        title = DirectLabel(text = "Connect 4!",
                            scale = 0.1,
                            pos = (0, 0, 0.9),
                            parent = self.titleMenu,
                            relief = None,
                            text_fg = (1, 1, 1, 1))
        title2 = DirectLabel(text = "in",
                             scale = 0.07,
                             pos = (0, 0, 0.79),
                             parent = self.titleMenu,
                             frameColor = (0.5, 0.5, 0.5, 1))
        title3 = DirectLabel(text = "3D !!",
                             scale = 0.125,
                             pos = (0, 0, 0.65),
                             parent = self.titleMenu,
                             relief = None,
                             text_fg = (1, 1, 1, 1))


        btn = DirectButton(text = "Two players ",
                           command = self.start_game,
                           pos = (0, 0, 0.2),
                           parent = self.titleMenu,
                           scale = 0.1,
                           frameSize = (-4, 4, -1, 1),
                           text_scale = 0.75,
                           relief = DGG.FLAT,
                           text_pos = (0, -0.2),
                           extraArgs=[True, False])
        btn.setTransparency(True)

        btn = DirectButton(text = "Play against AI",
                           command = self.setup_ai_screen,
                           pos = (0, 0, 0),
                           parent = self.titleMenu,
                           scale = 0.1,
                           frameSize = (-4, 4, -1, 1),
                           text_scale = 0.75,
                           relief = DGG.FLAT,
                           text_pos = (0, -0.2))
        btn.setTransparency(True)



    def start_game(self, multiplayer, ai, ai_stuff=[[-2], -2], was_on_ai_screen=False):


        self.camera.setPos(0, -self.cam_dist, 120)
        self.camera.lookAt(0, 0, 0)

        self.setup_grid()

        self.accept('mouse1', self.startDrop)

        self.titleMenu.hide()
        self.titleMenuBackdrop.hide()

        if was_on_ai_screen:
            self.aiScreen.hide()
        if ai is True:
            self.ai_playing = True

        ai_depths = [0, 1, 2, 5, 7]

        self.lvl = ai_stuff[0]
        self.ai_level = ai_depths[ai_stuff[0][0]]

        self.ai_color = ai_stuff[1]

        self.reset()

        self.taskMgr.add(self.__getMousePos, '_Connect4__getMousePos')
        self.taskMgr.add(self.cameraFancyRotation, 'cameraFancyRotation')
        self.taskMgr.add(self.rotateEarth, 'roateEarth')



    def reset(self):


        self.cameraTarget = 'left'
        self.angleDegrees = 0
        self._angleDegrees = 0
        self.angleRadians = 0
        self.cameraRotationType = 'fancy'

        self.cameraSide = 0
        self.refAngle = 0
        self.resetAngle= False

        if self.textNodePath is not None and self.rematchBtn is not None:
            self.textNodePath.removeNode()
            self.rematchBtn.destroy()


        for coin in self.coins:
            coin.removeNode()
            del coin
        self.coins = [self.newCoin('y')]
        self.currcoin = 0

        self.drop_row = -1

        self.turn = 0 # 0 ou 1

        self.gameOver = False
        self.isDropping = False
        self.vUp = 0

        self.eng = Connect4Engine() # to reset everything inside it






    def setup_ai_screen(self):

        v = [0]

        self.aiScreen = DirectDialog(frameSize=(-0.47, 0.7, -.7, .7),
                                        fadeScreen=.4,
                                        relief=DGG.FLAT)
        label = DirectLabel(text='Choose AI level: ',
                            parent=self.aiScreen,
                            scale=.07,
                            pos=(.1, 0, .7))

        buttons = [
            DirectRadioButton(text='Random', variable=v, value=[0],
                              scale=0.09, pos=(-.1, 0, .5), parent=self.aiScreen),
            DirectRadioButton(text='Level 1', variable=v, value=[1],
                              scale=0.09, pos=(-.1, 0, .3), parent=self.aiScreen),
            DirectRadioButton(text='Level 2', variable=v, value=[2],
                              scale=0.09, pos=(-.1, 0, .1), parent=self.aiScreen),
            DirectRadioButton(text='Level 3', variable=v, value=[3],
                              scale=0.09, pos=(-.1, 0, -.1), parent=self.aiScreen),
            DirectRadioButton(text='Level 4', variable=v, value=[4],
                              scale=0.09, pos=(-.1, 0, -.3), parent=self.aiScreen)
        ]

        labels = [
            DirectLabel(text='',
                    parent=self.aiScreen,
                    scale=.09,
                    pos=(.3, 0, .5)),
            DirectLabel(text='EZ',
                    parent=self.aiScreen,
                    scale=.09,
                    pos=(.2, 0, .3)),
            DirectLabel(text='Medium ',
                    parent=self.aiScreen,
                    scale=.09,
                    pos=(.3, 0, .1)),
            DirectLabel(text='Hard ',
                    parent=self.aiScreen,
                    scale=.09,
                    pos=(.2, 0, -.1)),
            DirectLabel(text='Impossible ',
                    parent=self.aiScreen,
                    scale=.09,
                    pos=(.35, 0, -.3))
        ]

        imgs = [
            OnscreenImage(image='./images/hankey.png', scale=.06,pos=(.27, 0, 0.52), parent=self.aiScreen),
            OnscreenImage(image='./images/relieved.png', scale=.05,pos=(.32, 0, 0.32), parent=self.aiScreen),
            OnscreenImage(image='./images/face_with_raised_eyebrow.png', scale=.05,pos=(.5, 0, 0.08), parent=self.aiScreen),
            OnscreenImage(image='./images/rage.png', scale=.05,pos=(.35, 0, -.08), parent=self.aiScreen),
            OnscreenImage(image='./images/innocent.png', scale=.05,pos=(.65, 0, -.28), parent=self.aiScreen),
        ]

        for button in buttons:
            button.setOthers(buttons) # so that you can only choose one button at a time


        btn = DirectButton(text = "Back",
                           command = self.aiScreen.hide,
                           pos = (-.2, 0, -.5),
                           parent = self.aiScreen,
                           scale = 0.1,
                           text_scale = 0.75,
                           relief = DGG.FLAT,
                           text_pos = (0, -0.2))

        btn = DirectButton(text = "Let's go!",
                           command = self.start_game,
                           pos = (.4, 0, -.5),
                           parent = self.aiScreen,
                           scale = 0.1,
                           text_scale = 0.75,
                           text_pos = (0, -0.2),
                           extraArgs=[False, True, [v, 1], True])



    def setup_grid(self):
        # create 6 vertical boxes, alternating between gray and light blue
        colors = [
            (115/255, 147/255, 179/255, .5),
            (128/255, 128/255, 128/255, .5)
        ]
        x_size = self.x_size
        start_x = -(3*x_size + 3*.7 + x_size/2)
        for i in range(8):
            _x = start_x + x_size*i
            rect_maker = createRect(
                width=3, height=x_size*6, depth=20, center=(_x, -20, -10), vertex_color=colors[i%2]
            )
            rect = self.render.attach_new_node(rect_maker.generate())
            #rect.set_render_mode_filled_wireframe((.666, 1, 0, .5)) # in case you want to it have the vertexes displayed
        bottomrect_maker = createRect(
            width=3.5, height=x_size*6+8*6, depth=25, center=(0, -20, -10), vertex_color=colors[1]
        )
        bottom_rect = self.render.attach_new_node(bottomrect_maker.generate())
        #bottom_rect.set_render_mode_filled_wireframe((0, .58, 1, .5))
        bottom_rect.set_r(90)
        bottom_rect.set_pos(8, 0, -80)



    def getDropCol(self):
        coin = self.coins[self.currcoin]
        col = -1
        for range in self.cols_xranges:
            if range[0] <= coin.getX() <= range[1]:
                col = range[2]
        if col != -1:
            return col


    def startDrop(self):



        curr_coin = self.coins[self.currcoin]
        self.stored_time = time()


        col = self.getDropCol()
        if col != None:
            if not self.isDropping and self.eng.is_valid_location(self.eng.board, col) and not self.gameOver and not self.cameraRotationType == 'turn':
                self.placeCoin(curr_coin, col)
                row = self.eng.get_next_open_row(self.eng.board, col)
                self.drop_row = row
                if self.turn == 0:
                    self.eng.drop_piece(self.eng.board, row, col, 1)
                elif self.turn == 1:
                    self.eng.drop_piece(self.eng.board, row, col, 2)
                self.isDropping = True
                self.taskMgr.add(self.processDrop, 'drop')







    def processDrop(self, task):




        curr_coin = self.coins[self.currcoin]

        dt = time()-self.stored_time



        if self.isDropping:
            curr_coin.setZ(curr_coin.getZ() + self.vUp*dt*0.3)
            self.vUp -= 1

        if curr_coin.getZ() < (-70+self.drop_row*self.x_size) and self.isDropping:
            self.endDrop()



        return task.again



    def endDrop(self):

        self.taskMgr.remove('drop')


        curr_coin = self.coins[self.currcoin]

        self.isDropping = False
        self.vUp = 0
        self.currcoin += 1


        self.cameraRotationType = 'turn'

        t = self.turn+1

        self.turn += 1
        self.turn = self.turn % 2

        if self.turn == 0:
            self.coins.append(self.newCoin('y'))
        elif self.turn == 1:
            self.coins.append(self.newCoin('r'))

        row = self.drop_row
        x_size = self.x_size
        curr_coin.setZ(-70+row*x_size)

        self.checkWin(t)







    def getMinimaxMove(self):

        curr_coin = self.coins[self.currcoin]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.eng.minimax, self.eng.board, self.ai_level, -float('inf'), float('inf'), True, 2, 1) # still to be ameliorated bc threading is kinda hard with panda3d :)
            col, minimax_score = future.result()


        row = self.eng.get_next_open_row(self.eng.board, col)
        self.drop_row = row
        self.placeCoin(curr_coin, col)

        self.eng.drop_piece(self.eng.board, row, col, 2)

        return col, minimax_score



    def aiPlay(self, task):

        curr_coin = self.coins[self.currcoin]

        if self.turn == self.ai_color and self.ai_playing and not self.gameOver:
            if self.ai_level == 0:
                col = choice(self.eng.get_valid_locations(self.eng.board))
                row = self.eng.get_next_open_row(self.eng.board, col)
                drop_row = row
                self.eng.drop_piece(self.eng.board, row, col, 2)
            else:
                col, minimax_score = self.getMinimaxMove()
                self.isDropping = True
                self.taskMgr.add(self.processDrop, 'drop')




        return task.done


    def placeCoin(self, coin, col):

        x_size = self.x_size
        start_x = -(2*x_size + 3*.7 + x_size/2)
        x_pos = start_x + x_size*col - x_size/2

        coin.setX(x_pos)


    def __getMousePos(self, task):

        curr_coin = self.coins[self.currcoin]
        if self.mouseWatcherNode.hasMouse() and not self.isDropping:
            mpos = self.mouseWatcherNode.getMouse()
            if self.cameraSide % 2 == 0:
                curr_coin.setX(mpos.x*200)
            else:
                curr_coin.setX(-mpos.x*200)


        return task.cont


    def newCoin(self, color):



        if color == 'y':
            c=(1, 1, 0, 1)
        else:
            c=(1, 0, 0, 1)
        coin_maker = createCylinder()
        coin = self.render.attachNewNode(coin_maker.generate())
        coin.set_render_mode_filled_wireframe(c)
        coin.set_p(90)
        coin.set_pos(-1.75, -20, 73.95)
        coin.set_scale(4, 4, 4)

        return coin



    def checkWin(self, piece):

        winner = ''

        win_result = self.eng.winning_move(self.eng.board, 1)
        if win_result:
            winner = 'Yellow'
        else:
            win_result = self.eng.winning_move(self.eng.board, 2)
            if win_result:
                winner = 'Red'
        if winner=='':
            coup_possible = False
            for col in range(7):
                coup_possible_temp = self.eng.is_valid_location(self.eng.board, col)
                coup_possible = coup_possible or coup_possible_temp
            if not coup_possible:
                winner = 'Nobody'

        if winner != '':
            self.text = TextNode('textnode')
            self.text.setText(winner + " Wins!!")
            self.textNodePath = self.aspect2d.attachNewNode(self.text)
            if winner == 'Yellow':
                self.textNodePath.setPos(-1, 0, 0.7)
            elif winner== 'Red':
                self.textNodePath.setPos(-.8, 0, 0.7)
            else:
                self.textNodePath.setPos(-1, 0, 0.7)
            self.textNodePath.setScale(0.3, 0.3, 0.3)
            self.gameOver = True






    def cameraFancyRotation(self, task):



        if self.cameraRotationType == 'fancy':
            if self.cameraTarget == 'left':
                self.angleDegrees-=0.08
                self._angleDegrees-=0.08
                self.angleRadians = self.angleDegrees * (pi / 180.0)
                if self._angleDegrees<-15:
                    self.cameraTarget = 'right'
            elif self.cameraTarget == 'right':
                self.angleDegrees+=0.08
                self._angleDegrees+= 0.08
                self.angleRadians = self.angleDegrees * (pi / 180.0)
                if self._angleDegrees>15:
                    self.cameraTarget = 'left'
        else:
                if not self.resetAngle:
                    self.refAngle = self._angleDegrees
                    self.resetAngle = True

                self.angleDegrees += 8.5
                self._angleDegrees += 8.5
                self.angleRadians = self.angleDegrees * (pi / 180.0)

                if self._angleDegrees>= self.refAngle+180:
                    self.cameraSide += 1
                    self.resetAngle = False
                    self.cameraRotationType = 'fancy'
                    self._angleDegrees -= 180

                    if not self.gameOver:
                        self.taskMgr.doMethodLater(2, self.aiPlay, 'aiPlay') # on attend 0.5 secondes avant que l'IA commence a jouer







        self.camera.setPos(self.cam_dist * sin(self.angleRadians), -self.cam_dist * cos(self.angleRadians), 20)
        self.camera.setHpr(self.angleDegrees, -7, 0) # to keep the camera looking at the grid


        return task.again



    def rotateEarth(self, task):

        self.earth.setHpr(self.earth, .03, .03, 0)

        return task.cont














game = Connect4()
game.run()