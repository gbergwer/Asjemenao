import basebehavior.behaviorimplementation

import time
import random
import almath


class FindBall_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    '''This behavior will move the Nao around until the ball is seen in the middle of the FoV.'''

    #this implementation should not define an __init__ !!!


    def implementation_init(self):
        self.__nao = self.body.nao(0)
        self.__nao.say("Find!")
        
        self.__start_time = time.time()
        self.__nao.complete_behavior("standup")
        #Make sure the robot is standing and looks horizontal:
        self.__nao.look_forward()
        self.__is_looking_horizontal = True

        #Possible states (WALK or TURN):
        self.__state = "FIND"
        self.__last_ball_recogtime = 0
        
        self.__wait = False


    def implementation_update(self):
        # Turn around in a certain direction unless you see the ball.
        # In that case, turn towards it until you have it fairly central in the Field of Vision.
        if (time.time() - self.__start_time) > 1 and not self.__wait:
            #self.__nao.start_behavior("AsjemeNao_Scan_Head")
            if (not self.__nao.isMoving()):
                #print "state: " + str(self.__state)
                if self.__state == "FIND":
                    self.__nao.look_forward()
                    self.__state = "FIND_FORWARD"
                elif self.__state == "FIND_FORWARD":
                    self.__nao.look_right()
                    self.__is_looking_horizontal = False
                    self.__state = "FIND_RIGHT"
                    #self.__nao.say("Looking Right")
                elif self.__state == "FIND_RIGHT":
                    self.__nao.look_forward()
                    self.__is_looking_horizontal = True
                    self.__state = "FIND_FORWARD2"
                    #self.__nao.say("Looking Straight forward")
                elif self.__state == "FIND_FORWARD2":
                    self.__nao.look_left()
                    self.__is_looking_horizontal = False
                    self.__state = "FIND_LEFT"
                    #self.__nao.say("Looking left")
                elif self.__state == "FIND_LEFT":
                    self.__is_looking_horizontal = False
                    self.__nao.look_forward_down()
                    self.__state = "FIND_DOWN_L"
                    #self.__nao.say("Looking down center")
                elif self.__state == "FIND_DOWN_L":
                    self.__state = "FIND_DOWN_M"
                    self.__nao.look_horizontal()
                    self.__is_looking_horizontal = True
                    #self.__nao.say("Looking down left") 
                elif self.__state == "FIND_DOWN_M":
                    self.__nao.look_right()
                    self.__is_looking_horizontal = False
                    self.__state = "FIND_DOWN_R"
                    #self.__nao.say("Looking down right")  
                elif self.__state == "FIND_DOWN_R":
                    self.__nao.look_forward()
                    self.__is_looking_horizontal = True
                    self.__state = "WALK_PREP"
                    #self.__nao.say("Looking forward again")                                                            
                elif self.__state == "WALK_PREP":
                    self.__nao.walkNav(0.2, 0, 0)
                    self.__state = "WALK"
                    #self.__nao.say("Looking forward, walking random")
                elif self.__state == "WALK":
                    self.__nao.walkNav(0, 0, (120 * almath.TO_RAD), 0.01)
                    self.__state = "FIND"
                    #self.__nao.say("Turning random")
                self.__nao.wait_for(0.5)

        #Try to see if there is a ball in sight:
        if (self.m.n_occurs("combined_red") > 0):
            (recogtime, obs) = self.m.get_last_observation("combined_red")
            if not obs == None and recogtime > time.time()-2:
                #print "red: x=%d, y=%d, size=%f" % (obs['x'], obs['y'], obs['size'])
                contours = obs["sorted_contours"]
                biggest_blob = contours[0]
                print "%s: x=%d, y=%d, width=%d, height=%d, surface=%d" \
                        % ("red", biggest_blob['x'], biggest_blob['y'], biggest_blob['width'], biggest_blob['height'], biggest_blob['surface'])
                self.__last_recogtime = recogtime
                #Ball is found if the detected ball is big enough (thus filtering noise):
                if biggest_blob['surface'] >30 and biggest_blob['surface'] < 500 and biggest_blob['width'] < 50 and biggest_blob['height'] < 50:
                    print "State: " + self.__state
                    print "Ball Detected"
                    #self.__wait = True
                    if self.__state == "FIND_RIGHT":
                        #self.__nao.say("Detected Right, now turning towards ball")
                        self.__nao.walkNav(0,0,-((45 + ((biggest_blob['x']-80)/80)*(30))) * almath.TO_RAD)
                        #normalisatie naar 1 (80/80), vervolgens naar graden (FOV camera = 60 deg, dus helft is 30 deg)
                        self.__state = "FIND_FORWARD"                      
                    elif self.__state == "FIND_LEFT":
                        #self.__nao.say("Detected Left, now turning towards ball")
                        self.__nao.walkNav(0,0,((45 + ((biggest_blob['x']-80)/80)*(-30))) * almath.TO_RAD)
                        #normalisatie naar 1 (-80/80), vervolgens naar graden (FOV camera = 60 deg, dus helft is 30 deg)
                        self.__state = "FIND_FORWARD" 
                                                                        
                    # Once the ball is properly found, use: self.m.add_item('ball_found',time.time(),{}) to finish this behavior.
                    if self.__state == "FIND_FORWARD" or self.__state == "FIND_FORWARD2":
                        self.__nao.look_forward() 
                        print "Looking forward"
                        #self.__nao.say("Now in front of the ball")
                        self.m.add_item('ball_found',time.time(),{})

                if biggest_blob['surface'] > 30 and biggest_blob['surface'] < 1500 and biggest_blob['width'] < 50 and biggest_blob['height'] < 50:
                    print "Ball Detected"
                    #self.__wait = True
                    if self.__state == "FIND_DOWN_L" and self.__is_looking_horizontal == True:
                        #self.__nao.say("Detected Left, now turning towards ball")
                        self.__nao.walkNav(0,0,((45 * almath.TO_RAD)+((biggest_blob['x']-80)*(-0.005))))
                        self.__nao.look_forward_down()
                        print "Looking forward down left"
                        self.__state = "FIND_FORWARD_DOWN"                        
                    elif self.__state == "FIND_DOWN_M":
                        #self.__nao.say("Detected in front of my feet")
                        self.__state = "FIND_FORWARD_DOWN"  
                    elif self.__state == "FIND_DOWN_R" and self.__is_looking_horizontal == True:
                        #self.__nao.say("Detected right, now turning towards ball")
                        self.__nao.walkNav(0,0,-((45 * almath.TO_RAD)+((biggest_blob['x']-80)*(-0.005))))
                        print "Angle: -" + string(((45 * almath.TO_RAD)+((biggest_blob['x']-80)*(-0.005))))
                        self.__nao.look_forward_down()
                        print "Looking forward down right"
                        self.__state = "FIND_FORWARD_DOWN"  
                                                                        
                    # Once the ball is properly found, use: self.m.add_item('ball_found',time.time(),{}) to finish this behavior.
                    if self.__state == "FIND_FORWARD_DOWN":
                        self.__nao.look_forward_down() 
                        print "Looking forward down ball found"
                        #self.__nao.say("Now in front of the ball")
                        self.m.add_item('ball_found',time.time(),{})
