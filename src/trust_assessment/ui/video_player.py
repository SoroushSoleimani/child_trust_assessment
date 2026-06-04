import cv2
import tkinter as tk
from PIL import Image, ImageTk
from typing import Optional

# ============================================================================
# VIDEO PLAYER UI COMPONENT
# ============================================================================
# This module implements a custom video player using OpenCV (cv2) and Tkinter.
# It plays video files (typically MP4) within a Tkinter canvas, providing
# basic playback and a "Skip Video" button. The player is used to show
# scenario videos to the child during the trust assessment test.
#
# Why OpenCV instead of VLC? OpenCV gives finer control over frame-by-frame
# rendering and is cross-platform, but it lacks audio support by default.
# For this application, videos are assumed to be silent or audio is not needed.
# Alternative: The earlier version used python-vlc; here OpenCV is used for simplicity.

class VideoPlayer:
    """
    A Tkinter-based video player that streams frames from a video file using OpenCV.
    
    The player displays video frames inside a Canvas widget at approximately 30 FPS
    (33 ms per frame). It also provides a "Skip Video" button that allows the child
    or administrator to bypass the current video and proceed immediately to the
    questions.
    
    Attributes:
        parent (tk.Tk or tk.Frame): The parent widget where the video will be shown.
        video_path (str): Full file path to the video file (e.g., "videos/girls/SEN1.mp4").
        on_complete (callable or None): Optional callback function to execute when
            the video finishes naturally or is skipped. It receives no arguments.
        cap (cv2.VideoCapture or None): OpenCV video capture object.
        canvas (tk.Canvas or None): Canvas widget that displays the video frames.
        running (bool): Flag indicating whether video playback is active.
        after_id (str or None): Identifier for the `after()` scheduled callback,
            used to cancel the frame update loop when stopping.
    """
    
    def __init__(self, parent, video_path: str, on_complete=None):
        """
        Initialize the video player but do not start playback immediately.
        
        Args:
            parent (tk.Tk or tk.Frame): The parent Tkinter widget (usually the main root window).
            video_path (str): Absolute or relative path to the video file.
            on_complete (callable, optional): Function to call when the video ends or is skipped.
                If None, nothing happens on completion.
        """
        self.parent = parent
        self.video_path = video_path
        self.on_complete = on_complete
        
        # OpenCV video capture object (created in play() method)
        self.cap = None
        
        # Canvas where video frames will be drawn
        self.canvas = None
        
        # Flag to control the frame update loop
        self.running = False
        
        # ID of the scheduled `after` callback (for cancellation)
        self.after_id = None
    
    def play(self):
        """
        Start playing the video.
        
        This method opens the video file using OpenCV, checks if it opened
        successfully, creates the UI (skip button), and begins the frame update loop.
        If the video cannot be opened, it immediately calls the on_complete callback
        (if provided) to allow the test to continue without the video.
        """
        # Attempt to open the video file
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            # If video file is missing or corrupted, skip it and proceed
            if self.on_complete:
                self.on_complete()
            return
        
        # Set the running flag to True to keep the update loop active
        self.running = True
        
        # Create the UI elements (currently just the skip button)
        self._create_ui()
        
        # Start the frame-by-frame rendering loop
        self._update_frame()
    
    def _create_ui(self):
        """
        Create and place the control buttons below the video canvas.
        
        Currently, only a "Skip Video" button is provided. Additional controls
        (play/pause, rewind) could be added here if needed.
        """
        # Frame to hold the control button(s) at the bottom of the parent window
        control_frame = tk.Frame(self.parent, bg="#2E7D64")
        control_frame.pack(side="bottom", pady=10)
        
        # "Skip Video" button – allows the child to bypass the current video
        skip_btn = tk.Button(control_frame, text="رد کردن ویدیو", 
                             command=self._skip_video, font=("B Nazanin", 14), 
                             bg="#FF9800", fg="white", padx=20, pady=5)
        skip_btn.pack()
    
    def _update_frame(self):
        """
        Read the next frame from the video and display it on the canvas.
        
        This method is called repeatedly via `parent.after()` to simulate
        real-time playback. It reads one frame, converts it from BGR (OpenCV
        default) to RGB, resizes it to fit the canvas (800x600), converts it to
        a PIL Image, then to a PhotoImage, and finally draws it on the canvas.
        
        If there are no more frames (video ends), it stops playback and calls
        the on_complete callback.
        """
        if not self.running:
            return
        
        # Read the next frame
        ret, frame = self.cap.read()
        if ret:
            # Convert color space: OpenCV uses BGR, Tkinter uses RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame to fit the canvas (800x600) while maintaining aspect ratio?
            # Here it is simply stretched to exactly 800x600. For better aesthetics,
            # aspect ratio preservation could be added, but this is simple.
            frame = cv2.resize(frame, (800, 600))
            
            # Convert the NumPy array (frame) to PIL Image, then to PhotoImage
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # If the canvas does not exist yet, create it
            if self.canvas is None:
                self.canvas = tk.Canvas(self.parent, width=800, height=600, bg="black")
                self.canvas.pack(pady=20)
            
            # Clear previous frame and draw the new one
            self.canvas.delete("all")
            self.canvas.create_image(400, 300, image=imgtk, anchor=tk.CENTER)
            
            # Keep a reference to prevent garbage collection
            self.canvas.image = imgtk
            
            # Schedule the next frame update after ~33 ms (approx 30 FPS)
            self.after_id = self.parent.after(33, self._update_frame)
        else:
            # Video has ended: stop playback and notify the callback
            self.stop()
            if self.on_complete:
                self.on_complete()
    
    def _skip_video(self):
        """
        Skip the current video and proceed to the next phase.
        
        This method is called when the "Skip Video" button is clicked.
        It stops the playback and invokes the on_complete callback so that
        the test can continue (usually to the question page).
        """
        self.stop()
        if self.on_complete:
            self.on_complete()
    
    def stop(self):
        """
        Stop video playback and release resources.
        
        This method:
            - Sets the running flag to False to halt the update loop.
            - Cancels any pending `after()` callbacks.
            - Releases the OpenCV VideoCapture object (freeing the video file).
            - Destroys the canvas widget (removing the video display).
        """
        self.running = False
        
        # Cancel the scheduled frame update if it exists
        if self.after_id:
            self.parent.after_cancel(self.after_id)
            self.after_id = None
        
        # Release the video capture object
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Remove the canvas widget from the window
        if self.canvas:
            self.canvas.destroy()
            self.canvas = None