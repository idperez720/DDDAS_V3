import numpy as np

class Sensor_Reconfigurator():
    def __init__(self, p1, p2, pid_controller):
        # Attack mitigation parameters
        self.ep1 = p1.reshape(-1) # x-y-phi, estimates Sensor1
        self.ep1[0:-1] = self.ep1[0:-1]/100
        self.ep2 = p2.reshape(-1) # x-y-phi, estimates robot
        self.ep2[0:-1] = self.ep2[0:-1]/100

        self.Q1 = np.array( [[0.1, 0, 0],[0, 0.1, 0],[0, 0, 0.1]] ) # EKF Q matrix - Sensor1
        self.Q2 = self.Q1.copy()     # EKF Q matrix - robot

        self.R1 = np.array( [[1, 0, 0],[0, 1, 0],[0, 0, 1]] ) # EKF Q matrix - Sensor1
        self.R2 = np.array( [[1, 0, 0],[0, 1, 0],[0, 0, 1]] ) # EKF Q matrix - robot

        self.P1 = np.array( [[1, 0, 0],[0, 1, 0],[0, 0, 1]] ) # EKF P matrix - Sensor1
        self.P2 = np.array( [[1, 0, 0],[0, 1, 0],[0, 0, 1]] ) # EKF P matrix - robot

        self.nu = np.array( [0.003, 0.003, 0.1305] ) # CUSUM discount factor
        self.tau = np.array( [0.8, 0.8, 4] ) # CUSUM threshold

        # # Attack mitigation variables initialization
        self.CUSUM_Sensor1 = np.zeros((3, 1)) # nuX, nuY, nuT
        self.CUSUM_Sensor2 = np.zeros((3, 1)) # tX, tY, tT

        self.alpha1 = np.zeros((3, 1))
        self.alpha2 = np.zeros((3, 1))

        self.alarm1 = 0
        self.alarm2 = 0

        # PID controller
        self._pid_controller = pid_controller

    def compute_convex_combination(self, p1, p2, r):

        u1 = self._pid_controller.compute_control_actions( p1, r )
        u2 = self._pid_controller.compute_control_actions( p2, r )
        p1 = p1.reshape(-1)
        p2 = p2.reshape(-1)
        u1 = u1.reshape(-1)
        u2 = u2.reshape(-1)
        p1[0:-1] = p1[0:-1]/100
        p2[0:-1] = p2[0:-1]/100
        self.ep1, self.P1 = self.ekf(p1, u1.copy(), self.ep1, self.P1, self.Q1, self.R1)
        self.ep2, self.P2 = self.ekf(p2, u2.copy(), self.ep2, self.P2, self.Q2, self.R2)

        residue1 = np.abs( p1 - self.ep1.reshape(-1) )
        residue2 = np.abs( p2 - self.ep2.reshape(-1) )

        tPosition = np.zeros((3, 1))
        for i in range(0, 3 ):
            self.CUSUM_Sensor1[i, 0] = self.cusum( self.CUSUM_Sensor1[i, 0], residue1[i], self.nu[i], self.tau[i] )
            self.CUSUM_Sensor2[i, 0] = self.cusum( self.CUSUM_Sensor2[i, 0], residue2[i], self.nu[i], self.tau[i] )
            print('s1',p1)
            print('s2',p2)
            self.alpha1[i] = 1 - self.CUSUM_Sensor1[i]/self.tau[i]
            self.alpha2[i] = 1 - self.CUSUM_Sensor2[i]/self.tau[i]
            if self.CUSUM_Sensor1[i]>= self.tau[i]:
                self.alarm1 = 1    
            if self.CUSUM_Sensor2[i]>= self.tau[i]:
                self.alarm2 = 1

        if self.alarm1 == 1:
            self.alpha1 = self.alpha1*0+0.0000001
            print('Attack detected on sensor 1!' )
        if self.alarm2 == 1:
            self.alpha2 = self.alpha2*0+0.0000001
            print('Attack detected on sensor 2!')
        for i in range(0, 3 ):
            if i == 0 or i == 1:
                m = 100
            else:
                m = 1
            tPosition[i] = ( p1[i]*self.alpha1[i] + p2[i]*self.alpha2[i] ) / (self.alpha1[i] + self.alpha2[i])*m

        return tPosition

    def ekf(self, y, u, xe, P, Q, R):
        dt = 0.1
        uAux = u.copy()
        uAux = u*0.154/(1100*0.0205)
        # print('u', uAux        )
        u[0] = (uAux[0] + uAux[1])*0.0205/2
        u[1] = -(uAux[0] - uAux[1])*(0.0205)/(0.053)
        xp = np.array( [  xe[0] + u[0]*np.cos( xe[2] + u[1]*dt/2 )*dt,
        xe[1] + u[0]*np.sin( xe[2] + u[1]*dt/2 )*dt,  xe[2] + u[1]*dt ])
        F = np.array( [ [ 1, 0, -u[0]*np.sin( xe[2] + u[1]*dt/2 )*dt ],
        [ 0, 1, u[0]*np.cos( xe[2] + u[1]*dt/2 )*dt ], [ 0, 0, 1 ] ] )
        P = np.matmul( np.matmul( F,P ), np.transpose( F ) ) + Q
        H = np.array( [[1, 0, 0], [0, 1, 0], [0, 0, 1]] )
        hxe = np.array( [ [xp[0]], [xp[1]], [xp[2]] ] )
        ye = y.reshape(3, 1) - hxe.reshape(3, 1)
        S = np.matmul( np.matmul( H, P ), np.transpose( H ) ) + R
        K = np.matmul( np.matmul( P, H ), np.linalg.inv( S ) )
        xe = xp.reshape(3, 1) + np.matmul( K, ye )
        P = np.matmul( H-np.matmul( K, H ), P )
        return xe.reshape(-1), P

    def cusum(self, CumSum, Residual, v, threshold):
        if CumSum >= threshold:
            CumSum = 0
        else:
            CumSum = np.clip( CumSum + Residual - v, 0, threshold)
        return CumSum
