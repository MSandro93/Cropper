import cv2
from os import listdir, getcwd
from os.path import isfile, exists
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import threading
import time


current_image = 0
files = []
x1_pos = 0          #current position of the left x-marker at the canvas
x2_pos = 0  
y1_pos = 0 
y2_pos = 0             
rotation = 0
mirror = False
cropped = 0

preview_width = 1040
preview_hight = 845
preview_ratio = preview_width / preview_hight

def updateSliderEvent(a):
    apply()                 # apply current marker position after manipulating markers by sliders manually. 

def bounderies_detect(img_):    # return:  x of valid area, y of valid area, w of valid area, h of valid area, width of whole image, height of whole image 
    gray = cv2.cvtColor(img_, cv2.COLOR_BGR2GRAY)

    _, threshold = cv2.threshold(gray, 32, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            best_cnt = cnt
        
    return (cv2.boundingRect(best_cnt), img_.shape[1], img_.shape[0] )

def updatePreview(f, angle: int, mirror: bool):
    img1 = Image.open(f[0])

    if(angle != 0):
        img1 = img1.rotate(angle, expand=True)

    if(mirror == True):
        img1 = ImageOps.mirror(img1)

    f[7] = img1.width   # save width of original image
    f[8] = img1.height  # save heigt of original image

    s_x, s_y = img1.size
    ratio = s_x/s_y
    if(ratio < preview_ratio):
        n_y = preview_hight
        n_x = round(n_y * ratio)

    else:
        n_x = preview_width
        n_y = round(n_x / ratio)

    img1 = img1.resize( (n_x, n_y) )
    img1 = ImageTk.PhotoImage(img1)

    canvas.itemconfig(image_container,image=img1)
    canvas.image = img1

    f[1] = n_x          # save width of preview image
    f[2] = n_y          # save heigt of preview image

def updateMarkers(f):  # position of marker X1 in the original image, position of marker X2 in the original image, position of marker Y1 in the original image, position of marker Y2 in the original image; width of the original image, height of the original image
    global x1_pos
    global x2_pos
    global y1_pos
    global y2_pos

    if(len(files)<1):
        return

    x_ratio = f[7] / f[1]             # calculate the ratio between width of the original picture and the displayed preview image
    y_ratio = f[8] / f[2]             # calculate the ratio between height of the original picture and the displayed preview image

    delta = int(round(f[3] / x_ratio)) - x1_pos           # Thus the move-function below moves the marker, relativ to it's current position, calculate the delta
    canvas.move(x1_bar, delta, 0)                       # move the marker to new position; area[0] = starting position of the valid reagion in the original picture
    x1_pos += delta                                     # update position of the marker

    delta = int(round( f[4] / x_ratio)) - x2_pos
    canvas.move(x2_bar, delta, 0)
    x2_pos += delta

    delta = int(round( f[5] / y_ratio)) - y1_pos
    canvas.move(y1_bar, 0, delta)
    y1_pos += delta

    delta = int(round( f[6] / y_ratio)) - y2_pos
    canvas.move(y2_bar, 0, delta)
    y2_pos += delta

def updateSliders():
    global x1_pos
    global x2_pos
    global y1_pos
    global y2_pos

    if(len(files)<1):
        return

    x1_slider.config(to_ = files[current_image][1]-1 )    # update maximum of slider
    x2_slider.config(to_ = files[current_image][1]-1 )    # update maximum of slider
    y1_slider.config(to_ = files[current_image][2]-1 )    # update maximum of slider
    y2_slider.config(to_ = files[current_image][2]-1 )    # update maximum of slider

    x_ratio = files[current_image][7] / files[current_image][1]             # calculate the ratio between width of the original picture and the displayed preview image
    y_ratio = files[current_image][8] / files[current_image][2]             # calculate the ratio between height of the original picture and the displayed preview image

    x1_pos = int(round(files[current_image][3] / x_ratio))
    x1_slider.set(x1_pos)
    x2_pos = int(round(files[current_image][4] / x_ratio))
    x2_slider.set(x2_pos)
    y1_pos = int(round(files[current_image][5] / y_ratio))
    y1_slider.set(y1_pos)
    y2_pos = int(round(files[current_image][6] / y_ratio))
    y2_slider.set(y2_pos)

    return 

def x1_slider_update(a):
    global x1_pos

    if(len(files)<1):
        return

    x1_ = x1_slider.get()
    delta = x1_ - x1_pos                                # Thus the move-function below moves the marker, relativ to it's current position, calculate the delta
    canvas.move(x1_bar, delta, 0)                       # move the marker to new position; area[0] = starting position of the valid reagion in the original picture
    x1_pos += delta                                     # update position of the marker

def x2_slider_update(a):
    global x2_pos

    if(len(files)<1):
        return

    x2_ = x2_slider.get()
    delta = x2_ - x2_pos                                # Thus the move-function below moves the marker, relativ to it's current position, calculate the delta
    canvas.move(x2_bar, delta, 0)                       # move the marker to new position; area[0] = starting position of the valid reagion in the original picture
    x2_pos += delta                                     # update position of the marker

def y1_slider_update(a):
    global y1_pos

    if(len(files)<1):
        return

    y1_ = y1_slider.get()
    delta = y1_ - y1_pos                                # Thus the move-function below moves the marker, relativ to it's current position, calculate the delta
    canvas.move(y1_bar, 0, delta)                       # move the marker to new position; area[0] = starting position of the valid reagion in the original picture
    y1_pos += delta                                     # update position of the marker

def y2_slider_update(a):
    global y2_pos

    if(len(files)<1):
        return

    y2_ = y2_slider.get()
    delta = y2_ - y2_pos                                # Thus the move-function below moves the marker, relativ to it's current position, calculate the delta
    canvas.move(y2_bar, 0, delta)                       # move the marker to new position; area[0] = starting position of the valid reagion in the original picture
    y2_pos += delta                                     # update position of the marker

def next():
    global current_image
    global rotation
    global mirror

    if(len(files)<1):
        return
    
    apply()

    current_image = current_image + 1                                           # update the position in the list of images
    if current_image >= len(files):
        current_image = len(files) - 1                                          # clip the position in the list of images to end of list

    updatePreview(files[current_image], files[current_image][9], files[current_image][10])                                         # update the displayed preview image with the new current one

    if(files[current_image][4] == -1):
        area, x_t, y_t = bounderies_detect( cv2.imread(files[current_image][0]) )   # perform detection of the black frame at the new current image; area_ list, consisting of the x and y position of the valid area, flowed by the total width and height of the image
        files[current_image][3] = area[0]
        files[current_image][4] = area[0]+area[2]
        files[current_image][5] = area[1]
        files[current_image][6] = area[1]+area[3]

    updateMarkers(files[current_image])
    updateSliders()            
    rotation  = 0
    mirror = False
    pos_cnt.config( text = str(current_image+1) + '/' + str(len(files)) )

def previous():
    global current_image
    global rotation
    global mirror

    if(len(files)<1):
        return
    
    apply()

    current_image = current_image - 1
    if current_image <= 0:
        current_image = 0

    updatePreview(files[current_image], files[current_image][9], files[current_image][10])
 
    if(files[current_image][4] == -1):
        area, x_t, y_t = bounderies_detect( cv2.imread(files[current_image][0]) )   # perform detection of the black frame at the new current image; area_ list, consisting of the x and y position of the valid area, flowed by the total width and height of the image
        files[current_image][4] = area[0]
        files[current_image][5] = area[0]+area[2]
        files[current_image][6] = area[1]
        files[current_image][7] = area[1]+area[3]

    updateMarkers(files[current_image])
    updateSliders()
    rotation  = 0
    mirror = False
    pos_cnt.config( text = str(current_image+1) + '/' + str(len(files)) )

def openDir():
    global files
    global current_image
    global rotation
    files.clear()

    path = dir_field.get()

    if( not exists(path)):
        return

    for d in listdir(path):
        if isfile(path + "\\" + d):
            if ( (d.lower().endswith('.jpg')) or (d.lower().endswith('.jpeg')) or (d.lower().endswith('.tif')) ):
                files.append(  [path + "\\" + d, -1, -1, -1, -1, -1, -1, -1, -1, 0, False]   )

        # files
        #       0: filename
        #       1: width of preview image
        #       2: height of preview image
        #       3: position of x1 border in original image
        #       4: position of x2 border in original image
        #       5: position of y1 border in original image
        #       6: position of y2 border in original image
        #       7: width of original image
        #       8: height of original image
        #       9: rotation
        #      10: mirror (False; True)

    current_image = 0


    updatePreview(files[current_image], 0, False)
    area, x_t, y_t = bounderies_detect( cv2.imread(files[current_image][0]) )   # perform detection of the black frame at the new current image; area_ list, consisting of the x and y position of the valid area, flowed by the total width and height of the image
    files[current_image][3] = area[0]
    files[current_image][4] = area[0]+area[2]
    files[current_image][5] = area[1]
    files[current_image][6] = area[1]+area[3]

    updateMarkers(files[current_image])
    updateSliders()
    rotation  = 0
    pos_cnt.config( text = str(current_image+1) + '/' + str(len(files)) )

    return
    
def selectDir():
    dir_field_text.set( filedialog.askdirectory() )
    
def crop(f_, outpath_, picsToCrop_):
    global cropped

    img_ = cv2.imread(f_[0])

    if(f_[9] == -90):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_CLOCKWISE)
    elif(f_[9] == 90):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif( abs(f_[9]) == 180 ):
        img_ = cv2.rotate(img_, cv2.ROTATE_180)
    elif(f_[9] == 270):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_CLOCKWISE)
    elif(f_[9] == -270):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_COUNTERCLOCKWISE)

    cv2.imwrite(outpath_, img_[f_[5]:f_[6], f_[3]:f_[4]], [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    lock = threading.Lock()

    lock.acquire()
    cropped += 1
    crop_cnt.config( text = str(cropped) + '/' + str(picsToCrop_) )
    lock.release()

def spinner(picsToCrop_):
    global cropped
    spinner = 0

    while cropped != picsToCrop_:
        text_ = "running"
        for i in range(spinner):
            text_ += '.'
        running_indicator.config( text = text_ )
        time.sleep(0.5)
        
        spinner += 1
        if spinner == 4:
            spinner = 0

    running_indicator.config( text = "")


def crop_all(): 
    global files
    global current_image
    global cropped

    apply()

    threads = []
    picsToCrop = 0
    cropped = 0

    if(len(files)<1):
        return

    for f in files:
        if(f[3] != -1):
            picsToCrop += 1

    crop_cnt.config( text = '0/' + str(picsToCrop) )

    for f in files:
        if(f[3] == -1):
            continue

        filename = '.'.join( f[0].split('.')[0:-1] ) + '.jpeg'

        threads.append( threading.Thread(target=crop, args=(f, filename, picsToCrop)) )
        threads[-1].start()

    s = threading.Thread(target=spinner, args=[picsToCrop])
    s.start()



    files.clear()
    threads.clear()
    current_image = 0
    canvas.image = None
    x1_slider.set(0)
    x2_slider.set(0)
    y1_slider.set(0)
    y2_slider.set(0)

    x1_pos = 0
    x2_pos = 0
    y1_pos = 0
    y2_pos = 0

    pos_cnt.config( text = "" )

    canvas.move(x1_bar, -x1_pos, 0)
    canvas.move(x2_bar, -x2_pos, 0)
    canvas.move(y1_bar, 0, -y1_pos)
    canvas.move(y2_bar, 0, -y2_pos)

def apply():

    if(len(files)<1):
        return

    x_ratio = files[current_image][7] / files[current_image][1]
    y_ratio = files[current_image][8] / files[current_image][2]

    files[current_image][3] = int(round(x1_slider.get() * x_ratio))
    files[current_image][4] = int(round(x2_slider.get() * x_ratio))
    files[current_image][5] = int(round(y1_slider.get() * y_ratio))
    files[current_image][6] = int(round(y2_slider.get() * y_ratio))

    files[current_image][9]  = rotation
    files[current_image][10] = mirror

def rot_left():
    global rotation
    global mirror

    if(len(files)<1):
        return

    rotation += 90
    if(rotation == 360):
        rotation = 0

    updatePreview(files[current_image], rotation, mirror)

    img_ = cv2.imread(files[current_image][0])
    if(rotation == -90):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_CLOCKWISE)
    elif(rotation == 90):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif( abs(rotation) == 180 ):
        img_ = cv2.rotate(img_, cv2.ROTATE_180)
    elif(rotation == 270):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_CLOCKWISE)
    elif(rotation == -270):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if(mirror == True):
        img_ = cv2.flip(img_, 1)

    area, x_t, y_t = bounderies_detect( img_ )
    files[current_image][3] = area[0]
    files[current_image][4] = area[0]+area[2]
    files[current_image][5] = area[1]
    files[current_image][6] = area[1]+area[3]

    updateMarkers(files[current_image])
    updateSliders() 

def rot_right():
    global rotation
    global mirror

    if(len(files)<1):
        return
    
    rotation -= 90
    if(rotation == 360):
        rotation = 0

    updatePreview(files[current_image], rotation, mirror)

    img_ = cv2.imread(files[current_image][0])
    if(rotation == -90):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_CLOCKWISE)
    elif(rotation == 90):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif( abs(rotation) == 180 ):
        img_ = cv2.rotate(img_, cv2.ROTATE_180)
    elif(rotation == 270):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_CLOCKWISE)
    elif(rotation == -270):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if(mirror == True):
        img_ = cv2.flip(img_, 1)

    area, x_t, y_t = bounderies_detect( img_ )
    files[current_image][3] = area[0]
    files[current_image][4] = area[0]+area[2]
    files[current_image][5] = area[1]
    files[current_image][6] = area[1]+area[3]

    updateMarkers(files[current_image])
    updateSliders() 

def mirror_func():
    global mirror

    if(len(files)<1):
        return

    if mirror == False:
        mirror = True
    else:
        mirror = False

    updatePreview(files[current_image], rotation, mirror)

    img_ = cv2.imread(files[current_image][0])
    if(rotation == -90):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_CLOCKWISE)
    elif(rotation == 90):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif( abs(rotation) == 180 ):
        img_ = cv2.rotate(img_, cv2.ROTATE_180)
    elif(rotation == 270):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_CLOCKWISE)
    elif(rotation == -270):
        img_ = cv2.rotate(img_, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if(mirror == True):
        img_ = cv2.flip(img_, 1)

    area, x_t, y_t = bounderies_detect( img_ )
    files[current_image][3] = area[0]
    files[current_image][4] = area[0]+area[2]
    files[current_image][5] = area[1]
    files[current_image][6] = area[1]+area[3]

    updateMarkers(files[current_image])
    updateSliders() 


window = Tk()
window.title("Cropper")
window.iconbitmap(getcwd() + '\\icon.ico')
window.geometry("1600x900")

openDir_butt = Button(window, text = "Open Directory",command=openDir)  
openDir_butt.place(height=25, width=100, x=1485, y=10)

SelctDir_butt = Button(window, text = "...",command=selectDir)  
SelctDir_butt.place(height=25, width=50, x=1425, y=10)  

# directory path input field
dir_field_text = StringVar()
dir_field = Entry(window, textvariable=dir_field_text)
dir_field.place(height=25, width=800, x=615, y=10)  

# preview image
canvas = Canvas(window, width=preview_width, height= preview_hight)
a = canvas.create_rectangle(0, 0,  preview_width, preview_hight, fill='gray')
canvas.move(a, 0, 0)
image_container = canvas.create_image(0,0, anchor="nw")
canvas.place(height=preview_hight, width=preview_width, x=545, y=45)

# markers
x1_bar = canvas.create_line(0, 0, 0, preview_hight, fill="red", width=1)
x2_bar = canvas.create_line(0, 0, 0, preview_hight, fill="red", width=1)
y1_bar = canvas.create_line(0, 0, preview_width, 0, fill="red", width=1)
y2_bar = canvas.create_line(0, 0, preview_width, 0, fill="red", width=1)


#sliders for border adjustments
x1_slider = Scale(window, from_=0, to_=3, label="left", showvalue=0, orient=HORIZONTAL, command=x1_slider_update)
x1_slider.place(width=485, x=20, y=95)
x1_slider.bind("<ButtonRelease-1>", updateSliderEvent)

x2_slider = Scale(window, from_=0, to_=3, label="right", showvalue=0, orient=HORIZONTAL, command=x2_slider_update)
x2_slider.place(width=485, x=20, y=140)
x2_slider.bind("<ButtonRelease-1>", updateSliderEvent)

y1_slider = Scale(window, from_=0, to_=3, label="top", showvalue=0, orient=HORIZONTAL, command=y1_slider_update)
y1_slider.place(width=485, x=20, y=230)
y1_slider.bind("<ButtonRelease-1>", updateSliderEvent)

y2_slider = Scale(window, from_=0, to_=3, label="bottom", showvalue=0, orient=HORIZONTAL, command=y2_slider_update)
y2_slider.place(width=485, x=20, y=275)
y2_slider.bind("<ButtonRelease-1>", updateSliderEvent)

# navigation buttons
next_butt = Button(window, text = "->",command=next)  
next_butt.place(height=25, width=50, x=455, y=45)

previos_butt = Button(window, text = "<-",command=previous)  
previos_butt.place(height=25, width=50, x=385, y=45)

# Crop-button
crop_butt = Button(window, text = "Crop all Images",command=crop_all)  
crop_butt.place(height=75, width=100, x=212, y=500)

# rotation Buttons
rot_left_img = PhotoImage(file=getcwd() + '\\rot_l.png')
rot_left_butt = Button(window, image=rot_left_img ,command=rot_left)
rot_left_butt.place(height=25, width=50, x=20, y=45)

rot_right_img = PhotoImage(file=getcwd() + '\\rot_r.png')
rot_left_butt = Button(window, image=rot_right_img ,command=rot_right)
rot_left_butt.place(height=25, width=50, x=90, y=45)

# mirror button
mirror_img = PhotoImage(file=getcwd() + '\\mirror.png')
mirror_butt = Button(window, image=mirror_img ,command=mirror_func)
mirror_butt.place(height=25, width=50, x=90+70, y=45)

# position label
pos_cnt = Label(window, text="")
pos_cnt.place(height=15, width=35, x=426, y=80)

# running indicator label
running_indicator = Label(window, text="", anchor='w')
running_indicator.place(height=15, width=70, x=244, y=585)

# crop cnt label
crop_cnt = Label(window, text="")
crop_cnt.place(height=15, width=35, x=244, y=585+30)

window.mainloop()