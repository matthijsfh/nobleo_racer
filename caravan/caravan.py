from ....linear_math import Transform

class caravan:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        
        # Initialize circular buffer with a fixed size of 10
        self.carPositionBuffer = [None] * 10  # Circular buffer of size 10
        self.carBufferIndex = 0               # Tracks the current position in the buffer
        self.is_buffer_full = False 


    # def initializeCarPosition(self, position: Transform, DEBUG):
    #     for i in range( len(self.carPositionBuffer)):
    #         self.carPositionBuffer[i] = position  

    #     if not DEBUG: return
        
    #     print(self.carPositionBuffer)

    #     return


    # def updateCarPosition(self, position: Transform):
    #     # Add the new position to the buffer at the current index
    #     self.carPositionBuffer[self.carBufferIndex] = position

    #     return
   
