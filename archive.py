import numpy as np
import matplotlib.pyplot as plt

def intometer(x):
    return 0.0254*x

####CONSTANTS:
RHO_PVC = 1380 #kg/m^3
GRAVITY = 9.81 #m/s^2
TIMESTEP = 0.5 #s
BE_EXTENSION_STEP = 0.006 #TODO: FILL IN WITH REAL VALUES LATER!!!!!

#input all dimensions as imperial!
class BuoyancyEngine:
    def __init__(self, id, od, cont_len, travel_len, laspeed, midpoint):
        self.id = intometer(id)
        self.od = intometer(od)
        self.cont_len = intometer(cont_len)
        self.travel_len = intometer(travel_len)
        self.laspeed = laspeed #m/s

        self.V_cont = 0.25*np.pi*self.od**2

        self.allowable_ext = midpoint

        self.mass = 1 #TODO: fill in

class PressureHull:
    def __init__(self,id,od,len,percent_stability):
        self.id = intometer(id)
        self.od = intometer(od)
        self.l_hull = len
        self.percent_stability = percent_stability
        
        self.stability = percent_stability*self.od
        self.V_hull = 0.25*np.pi*self.od**2

        #self.mass = RHO_PVC*(np.pi*())

def seaglider_trajectory(rho_water, be, hull, midpoint, m_glider, hfoil_coeff):
    max_speed = 0
    glide_period = 0
    output_arr = []


    ###iteratively solve BE extension distances w sim in first while loop

    max_allowable_depth = -20 #m
    sim_depth = 0 #m

    ###remember to save the final valid numbers, probably use a break statement
    while(sim_depth > max_allowable_depth):
        ####START Trajectory Sim in second while loop 
        ###SETUP CONSTANTS
        s_y_prev = 0 #m
        s_y = 0 #m
        s_x_prev = 0 #m
        s_x = 0 #m

        v = 1 #m/s
        #v_y_prev = 0.00001 #m/s
        #v_x_prev = v #m/s --> starting from top so all velocity in x

        v_x_arr = []
        max_speed = 0

        s_x_arr = []
        s_y_arr = []
        s_x_change_down_arr = []
        s_x_change_up_arr = []

        time_arr = []
        be_pos_arr = []
        #--> going down (L+)
        L = 0.5*rho_water*hfoil_coeff*v**2


        #setup current_len
        current_len = midpoint
        time = 0

        diving = True
        contunuing_criteria = True
        while (contunuing_criteria == True):
            #calc be volume
            V_be = be.V_cont + (0.25*np.pi*be.id**2)*current_len

            #solve glide angle
            theta = np.arctan( ( hull.l_hull * (rho_water*GRAVITY*(0.25*np.pi*be.id**2)*current_len) ) / (m_glider*GRAVITY*hull.stability) )

            #solve Fy, Fx
            if(s_y <= s_y_prev):
                F_y = rho_water*GRAVITY*(hull.V_hull + V_be ) - m_glider*GRAVITY + L*np.sin(theta)
            else:
                F_y = rho_water*GRAVITY*(hull.V_hull + V_be ) - m_glider*GRAVITY - L*np.sin(theta)
            
            F_x = L*np.cos(theta) #NOTE: Tried adding 0.7 to sim drag this worked, separate term seemed to nuke simnot sure????

            #print(rho_water*GRAVITY*(hull.V_hull + V_be ), m_glider*GRAVITY, L*np.sin(theta), F_y)
            #print(s_x, F_y)

            #"integrate" w timestep
            v_y = (F_y/m_glider)*TIMESTEP
            v_x = (F_x/m_glider)*TIMESTEP

            v_x_arr.append(v_x)
            print(v_x)

            #print(v_y,v_x)

            s_y = s_y_prev + v_y
            s_x = s_x_prev + v_x

            s_x_arr.append(s_x)
            s_y_arr.append(s_y)

            s_y_prev = s_y
            s_x_prev = s_x


            if( current_len <= (midpoint - be.allowable_ext) and diving == True):
                diving = False
                s_x_change_up_arr.append(s_x)
                #print("going up", s_x)

            if( current_len >= (midpoint + be.allowable_ext) and diving == False):
                diving = True
                contunuing_criteria = False
                s_x_change_down_arr.append(s_x)
                #print("going down", s_x)

            if diving == True:
                current_len -= be.laspeed*TIMESTEP
            else:
                current_len += be.laspeed*TIMESTEP

            #print(theta, F_y, v_y, v_x, s_x, current_len)
            time = time + TIMESTEP
            time_arr.append(time)
            be_pos_arr.append(39.3701*current_len)


        plt.subplot(1,2,1)  
        plt.plot(s_x_arr, s_y_arr, label='Seaglider Position', color='blue')
        for i in s_x_change_down_arr:
            plt.axvline(x=i, color='r', linestyle='--', label='change up')
        for i in s_x_change_up_arr:
            plt.axvline(x=i, color='g', linestyle='--', label='change up')

        plt.xlabel('X-Pos (m)')
        plt.ylabel('Y-Pos (m)')

        plt.subplot(1,2,2)
        plt.plot(s_x_arr, be_pos_arr, label='BE Position Over X-Pos', color='blue')
        plt.xlabel('X-Pos (m)')
        plt.ylabel('B.E. Pos (m)')
        plt.show()

        
        sim_depth = np.min(s_y_arr)
        max_speed = np.max(v_x_arr)
        glide_period = (4/3)*s_x_arr[-1]

        #after sim check max allowable depth. If we havent hit save, if we have break out of while loop
        #if(sim_depth < max_allowable_depth):
        #    be.allowable_ext = max_be_extension

        ###iterate!!!!!
        be.allowable_ext+= BE_EXTENSION_STEP

        #print(sim_depth)


    print("allowable extension: ",be.allowable_ext)
    print("max fwd speed: ",max_speed)
    print("glide period: ",glide_period)

    output_arr.append(be.allowable_ext)
    output_arr.append(max_speed)
    output_arr.append(glide_period)

    output_arr.append(be)
    output_arr.append(hull)
    return output_arr




####inputs:
hfoil_coeff = 0.008 #Area of wing * Coeff Lift
percent_stability = 0.2 #%
rho_water =1003 #kg/m^3
midpoint = intometer(4)

#geometry
buoyeng = BuoyancyEngine( 3.25,3.5,10.3, 8, 0.08*0.0254,midpoint)
preshull = PressureHull( 4.0, 4.5, 0.9617564725, percent_stability)

m_glider = rho_water*(preshull.V_hull+buoyeng.V_cont + (0.25*np.pi*(buoyeng.od)**2) *midpoint)
#17.625 rho_water*(preshull.V_hull+buoyeng.V_cont + (0.25*np.pi*(buoyeng.id)**2) *buoyeng.travel_len*0.5)
#print(m_glider, m_glider*GRAVITY,GRAVITY*rho_water*(preshull.V_hull+buoyeng.V_cont + (0.25*np.pi*(buoyeng.id)**2) *buoyeng.travel_len*0.5) )

print(m_glider, midpoint)
seaglider_trajectory(rho_water, buoyeng, preshull, midpoint, 1.01*m_glider, hfoil_coeff)
print(39.3701*buoyeng.allowable_ext)
