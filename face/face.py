import tkinter as tk
from tkinter import Tk
import os

class Face(tk.Tk):
    """
    Face for the BinButler
    """
    def __init__(self, start_state: str = "sleep", FRAME_RATE: int = 10, HEIGHT: int = 480, WIDTH: int = 800):
        """

        args:
            start_state: str
                The starting state of the face. Options are:
                "happy", "moving", "sleep", "thankyou"
            
            NUM_FRAMES: int
        """
        super().__init__(className="Face animator")
        
        # the title of the window
        self.title("BinButler")

        # the size of the window
        self.HEIGHT = HEIGHT
        self.WIDTH = WIDTH

        # the emotions of the face
        self.current_emotion = start_state

        # get the number of pngs in the folder
        NUM_FRAMES_H = len([name for name in os.listdir(f"faces/happy") if ".png" in name])
        NUM_FRAMES_M = len([name for name in os.listdir(f"faces/moving") if ".png" in name])
        NUM_FRAMES_S = len([name for name in os.listdir(f"faces/sleep") if ".png" in name])
        NUM_FRAMES_T = len([name for name in os.listdir(f"faces/thankyou") if ".png" in name])

        print("Loading faces...")
        self.emotions = {
            "happy": [tk.PhotoImage(file=f"faces/happy/frame_{frame:05d}.png") for frame in range(1, NUM_FRAMES_H+1)],
            "moving": [tk.PhotoImage(file=f"faces/moving/frame_{frame:05d}.png") for frame in range(1, NUM_FRAMES_M+1)],
            "sleep": [tk.PhotoImage(file=f"faces/sleep/frame_{frame:05d}.png") for frame in range(1, NUM_FRAMES_S+1)],
            "thankyou": [tk.PhotoImage(file=f"faces/thankyou/frame_{frame:05d}.png") for frame in range(1, NUM_FRAMES_T+1)]
        }
        
        # the canvas for the face
        self.canvas = tk.Canvas(self, width=HEIGHT, height=WIDTH, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        
        # setting up the fullscreen
        self.bind("<F11>", self.toggle_fullscreen)
        self.fullscreen = False

        # running fullscreen on start
        self.toggle_fullscreen()
	
        # frame rate
        self.frame_rate = FRAME_RATE

        # timer from animations
        self.frame_counter = 0

        # creating the face initial image
        self.face = self.canvas.create_image(0, 0, image=self.emotions[self.current_emotion][self.frame_counter], anchor="nw")

        # update the frame
        self.update_frame()
        
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)
        return "done"

    def change_emotion(self, new_emotion: str):
        """
        Changes the emotion of the face

        args:
            new_emotion: str
                The new emotion of the face. Options are:
                "happy", "moving", "sleep", "thankyou"
        """
        # handle thankyou frame rate
        if new_emotion == "thankyou": self.frame_rate = 8
        else : self.frame_rate = 12
        if new_emotion in self.emotions: self.current_emotion = new_emotion
        self.frame_counter = 0
        print(f"Changing emotion to {new_emotion}")

    def update_frame(self):
        """
        Updates the frame of the animation
        """
        # delete the previous image
        # self.canvas.delete("all")
        # self.canvas.create_image(self.WIDTH/2, self.HEIGHT/2, image=self.emotions[self.current_emotion][self.frame_counter])
        self.canvas.itemconfig(self.face, image=self.emotions[self.current_emotion][self.frame_counter])
        self.frame_counter = (self.frame_counter + 1) % len(self.emotions[self.current_emotion])
        self.after(1000 // self.frame_rate, self.update_frame)
