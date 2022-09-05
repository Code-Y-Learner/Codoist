from tkinter import *
import math
import itertools
# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
reps = 0
timer = None
pause = False
toggle_pause_unpause = itertools.cycle(["pause","unpause"])

# ---------------------------- TIMER RESET ------------------------------- # 
def reset_timer():
    window.after_cancel(timer)
    logo.config(text='Timer',fg=GREEN)
    canvas.itemconfig(timer_text,text="00:00")
    check.config(text='')
    global  reps
    reps = 0


# ---------------------------- TIMER MECHANISM ------------------------------- # 
def start_timer():
    global reps
    reps += 1
    work_sec = WORK_MIN* 60
    short_break_sec = SHORT_BREAK_MIN *60
    long_break_sec = LONG_BREAK_MIN* 60
    if reps ==8:
        count_down(long_break_sec)#long
        logo.config(text='Finish',fg=RED)
        reset_timer()
    elif reps % 2 ==0:
        count_down(short_break_sec)#short_break_sec
        logo.config(text='Break',fg=PINK)
    else:
        count_down(work_sec)#work_sec
        logo.config(text='Work',fg=GREEN)


def on_pause_unpause_button_clicked():
    action = next(toggle_pause_unpause)
    if action == 'pause':
        global pause
        pause = True
    elif action == 'unpause':
        pause = False



# ---------------------------- COUNTDOWN MECHANISM ------------------------------- # 
def count_down(count):
    global reps
    count_min = math.floor(count / 60)
    count_sec = count % 60
    if count_sec < 10:
        count_sec = '0'+str(count_sec)
    if count_sec ==0:
        count_sec ='00'

    canvas.itemconfig(timer_text,text = f"{count_min}:{count_sec}")
    if count >0:
        global timer
        if pause == False:
            timer = window.after(1000,count_down,count - 1)
        elif pause == True:
            timer =  window.after(1000,count_down,count)
    else:
        start_timer()
        check_time = math.floor((reps-1) / 2)
        check.config(text = '✓'*check_time)



# ---------------------------- UI SETUP ------------------------------- #


window = Tk()
window.title('Pomodoro')
window.config(padx=100,pady=50,bg=YELLOW)

#canvas
canvas = Canvas(width=200,height=224,bg=YELLOW, highlightthickness=0)
tomato_img = PhotoImage(file='./tomato.png')
canvas.create_image(100,112,image=tomato_img)
timer_text = canvas.create_text(100,130,text='00:00',fill='white',font=(FONT_NAME,35,'bold'))
canvas.grid(column=1,row=1)



#label
logo = Label(text='Timer',fg=GREEN,bg=YELLOW,font=(FONT_NAME,40,'bold'))
logo.grid(column=1,row=0)

check = Label(bg=YELLOW,fg=GREEN,font=(FONT_NAME,15))
check.grid(column=1,row=3)
#button
start_button = Button(text='Start',command=start_timer,highlightthickness=0)
start_button.grid(column=0,row=2)

reset_button = Button(text='Reset',command=reset_timer,highlightthickness=0)
reset_button.grid(column=2,row=2)

pause_button = Button(text='pause',command=on_pause_unpause_button_clicked,highlightthickness=0)
pause_button.grid(column=1,row=2)

# pause
# toggle_pause_unpause = itertools.cycle(["pause","unpause"])


window.mainloop()