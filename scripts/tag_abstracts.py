import tkinter as tk
import gui_tagger

def main():
    """
    Initializes and runs the literature tagging GUI.
    """
    root = tk.Tk()
    root.title("Literature Tagger")
    root.geometry("1200x800")
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
