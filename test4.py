import pygame
import math
import numpy as np
import random


pygame.init()

screen = pygame.display.set_mode((400,400))
screen.fill((0,0,0))
pygame.display.set_caption("Electrostatics")
clock = pygame.time.Clock()

font = pygame.font.SysFont('Arial', 10, bold=True)  

normalpt = font.render('•', True,
            pygame.Color(100, 100, 100, 225),
            pygame.Color(0, 0, 0, 0))

mainpt = font.render('@', True,
            pygame.Color(255, 225, 255, 225),
            pygame.Color(0, 0, 0, 0))


# Parametric form of sphere (r, theeta, phi)
def GetPtOnSp(r,t,p):
    x = r*np.sin(p)*np.cos(t)
    y = r*np.cos(p)
    z = r*np.sin(p)*np.sin(t)
    return (x,y,z)

def GeneratePoints(R):
    density = 0.1
    #number of points = density x length
    pnum = np.linspace(0, 2*np.pi, math.ceil(density*2*np.pi*R))
    points = []
    for p in pnum:
        r = abs(R*np.sin(p))
        tnum = np.linspace(0, 2*np.pi, math.ceil(density*2*np.pi*r))
        for t in  tnum:
            points.append(GetPtOnSp(R,t,p))
    return points

# Flatten 3D points to 2D points while considering prespective 
def TransformPoints(points):
    tpoints = []
    focal_dist = 600
    for point in points:
        if point[2] != 0:
            xt = point[0]*focal_dist/(point[2] - 200) 
            yt = point[1]*focal_dist/(point[2] - 200)
        else:
            xt = point[0] 
            yt = point[1] 
        tpoints.append((xt, yt))
    return tpoints

# Rotate all the points by certian angle around x-axis using matrix transformation (rotation matrix)
def RotateX(points, angle):
    if angle == 0:
        return points
    rpoints = []
    for point in points:
        x = point[0]
        y = point[1]*math.cos(angle) - point[2]*math.sin(angle)
        z = point[1]*math.sin(angle) + point[2]*math.cos(angle)
        rpoints.append((x,y,z))
    return rpoints

# Rotate all the points by certian angle around y-axis using matrix transformation (rotation matrix)
def RotateY(points, angle):
    if angle == 0:
        return points
    rpoints = []
    for point in points:
        x = point[0]*math.cos(angle) + point[2]*math.sin(angle)
        y = point[1]
        z = -point[0]*math.sin(angle) + point[2]*math.cos(angle)
        rpoints.append((x,y,z))
    return rpoints

# Takes in 3D parametric form of coordinates on the sphere, rotates them about x and y axes, and flatten them into 2D using perspective
def GetXY(r, t, p):
    # 1.convert parametric form into cartesian form        
    cor = GetPtOnSp(r, t, p)
    # 2.rotate them about x-acis and then y-axis        
    rcor = RotateY([RotateX([cor], ax)[0]], ay)[0]
    # 3.transform the points into 2D         
    tcor = TransformPoints([rcor])[0]
    return tcor

# Calculate distance between two points on the sphere
def CalcDist(p1, p2):
    x1 = p1[0]*math.sin(p1[2])*math.cos(p1[1])
    y1 = p1[0]*math.cos(p1[2])
    z1 = p1[0]*math.sin(p1[2])*math.sin(p1[1])

    x2 = p2[0]*math.sin(p2[2])*math.cos(p2[1])
    y2 = p2[0]*math.cos(p2[2])
    z2 = p2[0]*math.sin(p2[2])*math.sin(p2[1])

    d = ((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)**1/2
    return d

# Find the gradient of the potential function (V = 1/d) in terms of angle "theeta" (t) and "phi" (p)
def Gradient(points, point):
    dp = 0
    dt = 0
    pt = point
    r = pt[0]
    t = pt[1]
    p = pt[2]
             
    for poi in points:
        if poi != point: 
            x1 = poi[0]*math.sin(poi[2])*math.cos(poi[1])
            y1 = poi[0]*math.cos(poi[2])
            z1 = poi[0]*math.sin(poi[2])*math.sin(poi[1])
            d = CalcDist(poi, pt)
            # partial derivativ of V=1/d (where d is the distance between two charges, and is a function of "theeta"(t) and "phi"(p)) wrt angle "phi" (p) = -1/d^2 * ∂(d)/∂p           
            dp += (-(x1 - r*math.sin(p)*math.cos(t))*math.cos(p)*math.cos(t) + (y1 - r*math.cos(p))*math.sin(p) - (z1 - r*math.sin(p)*math.sin(t))*math.cos(p)*math.sin(t))/d*(1/d)
            #print("hey")
            # partial derivativ of V=1/d (where d is the distance between two charges, and is a function of "theeta"(t) and "phi"(p)) wrt angle "theeta" (t) = -1/d^2 * ∂(d)/∂t                 
            dt += ((x1 - r*np.sin(p)*np.cos(t))*np.sin(p)*np.sin(t) - (z1 - r*np.sin(p)*np.sin(t))*np.sin(p)*np.cos(t))/d*(1/d)

    # Return the gradient (Gradient -> [∂(v)/∂t, ∂(v)/∂p] vector)    
    return (dt, dp)

# Generate the plot points "." on sphere
plotpoints = GeneratePoints(50)


ax = 0.8
ay = np.pi/4

# Number of charges 
chargenum = 5

# creates a list of charges (list containes -> coordinates of charges)
charges = []
for i in range(0, chargenum):
    charge = (50, random.uniform(0,2*np.pi), random.uniform(0,2*np.pi))
    charges.append(charge)
            
avg = 0
move = True
running = True

while running:
    # Check for Quit         
    for event in pygame.event.get():
        if event.type == pygame.QUIT or pygame.KEYDOWN == pygame.K_ESCAPE:
            pygame.quit()
            running = False
    if running == False:
        break
            

    # Clear Screen to remove old points
    screen.fill((0,0,0))

    # Render Plot points on sphere
    rpoints = RotateX(plotpoints, ax)
    rpoints = RotateY(rpoints, ay)
    tpoints = TransformPoints(rpoints)
    for point in tpoints:
        screen.blit(normalpt, (point[0] + screen.get_size()[0]/2, point[1] + screen.get_size()[1]/2))
         
    # Render Charges on sphere
    sum= 0
    for charge in charges:
                
        # Get the flattened 2D coordinates of the charges    
        chargexy = GetXY(r=charge[0], t=charge[1], p=charge[2])
                
        # Render the chrages on the screen        
        screen.blit(mainpt, (chargexy[0] + screen.get_size()[0]/2, chargexy[1] + screen.get_size()[1]/2))
        grad = Gradient(charges, charge)
        dt = grad[0]
        dp = grad[1]
                
        # move the charge to a new place by changing it's "theeta" and "phi" angles, using the gradient        
        if move:
            chargenew = (charge[0], charge[1]+ dt*5000, charge[2]+ dp*5000)
            charges[charges.index(charge)] = chargenew
        sum += dp+dt

    avg = sum/len(charge)
    # if the average of all the changes required to minimize energy is very small, we have a good enough appriximation and we stop moving the charges        
    if abs(avg) < 10**-10 and move == True:
        move = False
        print("Done!") 
    

    #screen.blit(mainpt, (tcor[0] + screen.get_size()[0]/2, tcor[1] + screen.get_size()[1]/2))

    # incrementing the angle by which all the points rotate about x and y axes            
    ax += 0.007
    ay += 0.005
    if ax >= 2*np.pi:
        ax = 0
    if ay >= 2*np.pi:
        ay = 0

    # set frame rate        
    clock.tick(50)

    pygame.display.update()



#print(type(np.linspace(0, np.pi, 10)))
