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


    # def getOldestPosition(self):
    #     # If the buffer is not full, the oldest position is at index 0
    #     if not self.is_buffer_full:
    #         return self.carPositionBuffer[0]
        
    #     # If the buffer is full, the oldest position is the next to be overwritten
    #     oldest_index = self.buffer_index
    #     return self.carPositionBuffer[oldest_index]


    def initializeCarPosition(self, position: Transform, DEBUG):
        for i in range( len(self.carPositionBuffer)):
            self.carPositionBuffer[i] = position  

        if not DEBUG: return
        print(self.carPositionBuffer)

        return


    def updateCarPosition(self, position: Transform):
        # Add the new position to the buffer at the current index
        self.carPositionBuffer[self.carBufferIndex] = position
        
        # # Move the index forward, wrapping around using modulo for circular behavior
        # self.carBufferIndex = (self.carBufferIndex + 1) % len(self.carPositionBuffer)
        
        # # If the buffer is full, update the flag
        # if self.carBufferIndex == 0:
        #     self.is_buffer_full = True

        return
   

    
    
    # def getPositionHistory(self):
    #     # Return the entire position buffer (note: it may contain None values initially)
    #     return self.carPositionBuffer