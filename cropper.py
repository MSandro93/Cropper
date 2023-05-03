import cv2
from os import listdir, getcwd
from os.path import isfile, exists
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk


current_image = 0
files = []
x1_pos = 0          #current position of the left x-marker at the canvas
x2_pos = 0  
y1_pos = 0 
y2_pos = 0             
rotation = 0

def bounderies_detect(img_):    # return:  x of valid area, y of valid area, w of valid area, h of valid area, width of whole image, height of whole iamge 
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

def updatePreview(f, angle):
    img1 = Image.open(f[0])

    if(angle != 0):
        img1 = img1.rotate(angle)

    f[7] = img1.width   # save width of original image
    f[8] = img1.height  # save heigt of original image

    s_x, s_y = img1.size
    ratio = s_x/s_y
    if(s_x > s_y):
        n_x = 1040
        n_y = int(n_x / ratio)

    else:
        n_y = 845
        n_x = int(n_y * ratio)

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

    if(len(files)<1):
        return

    current_image = current_image + 1                                           # update the position in the list of images
    if current_image >= len(files):
        current_image = len(files) - 1                                          # clip the position in the list of images to end of list

    updatePreview(files[current_image], files[current_image][9])                                         # update the dispalyed preview image with the new current one

    if(files[current_image][4] == -1):
        area, x_t, y_t = bounderies_detect( cv2.imread(files[current_image][0]) )   # perform detection of the black frame at the new current image; area_ list, consisting of the x and y position of the valid area, flowed by the total width and height of the image
        files[current_image][3] = area[0]
        files[current_image][4] = area[0]+area[2]
        files[current_image][5] = area[1]
        files[current_image][6] = area[1]+area[3]

    updateMarkers(files[current_image])
    updateSliders()            
    rotation  = 0
    pos_cnt.config( text = str(current_image+1) + '/' + str(len(files)) )

def previous():
    global current_image
    global rotation

    if(len(files)<1):
        return

    current_image = current_image - 1
    if current_image <= 0:
        current_image = 0

    updatePreview(files[current_image], files[current_image][9])
 
    if(files[current_image][4] == -1):
        area, x_t, y_t = bounderies_detect( cv2.imread(files[current_image][0]) )   # perform detection of the black frame at the new current image; area_ list, consisting of the x and y position of the valid area, flowed by the total width and height of the image
        files[current_image][4] = area[0]
        files[current_image][5] = area[0]+area[2]
        files[current_image][6] = area[1]
        files[current_image][7] = area[1]+area[3]

    updateMarkers(files[current_image])
    updateSliders()
    rotation  = 0
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
                files.append(  [path + "\\" + d, -1, -1, -1, -1, -1, -1, -1, -1, 0]   )

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

    current_image = 0


    updatePreview(files[current_image], 0)

    area, x_t, y_t = bounderies_detect( cv2.imread(files[current_image][0]) )   # perform detection of the black frame at the new current image; area_ list, consisting of the x and y position of the valid area, flowed by the total width and height of the image
    files[current_image][3] = area[0]
    files[current_image][4] = area[0]+area[2]
    files[current_image][5] = area[1]
    files[current_image][6] = area[1]+area[3]

    updateMarkers(files[current_image])
    updateSliders()
    rotation  = 0
    pos_cnt.config( text = str(current_image+1) + '/' + str(len(files)) )
    
def selectDir():
    dir_field_text.set( filedialog.askdirectory() )
    
def crop_all():
    global files
    global current_image

    if(len(files)<1):
        return

    pos_cnt.config( text = '0/' + str(len(files)) )

    for f in files:
        if(f[3] == -1):
            continue
        img_ = cv2.imread(f[0])
        x1_ = f[3]
        x2_ = f[4]
        y1_ = f[5]
        y2_ = f[6]

        if(f[9] == -90):
            img_ = cv2.rotate(img_, cv2.ROTATE_90_CLOCKWISE)
        elif(f[9] == 90):
            img_ = cv2.rotate(img_, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif( abs(f[9]) == 180 ):
            img_ = cv2.rotate(img_, cv2.ROTATE_180)
        elif(f[9] == 270):
            img_ = cv2.rotate(img_, cv2.ROTATE_90_CLOCKWISE)
        elif(f[9] == -270):
            img_ = cv2.rotate(img_, cv2.ROTATE_90_COUNTERCLOCKWISE)

        filename = f[0].split('.')[0] + '.jpeg'

        cv2.imwrite(filename, img_[y1_:y2_, x1_:x2_], [int(cv2.IMWRITE_JPEG_QUALITY), 100])


    files.clear()
    current_image = 0
    canvas.image = None
    x1_slider.set(0)
    x2_slider.set(0)
    y1_slider.set(0)
    y2_slider.set(0)

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

    files[current_image][9] = rotation

def rot_left():
    global rotation

    if(len(files)<1):
        return

    rotation += 90
    if(rotation == 360):
        rotation = 0

    updatePreview(files[current_image], rotation)

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

    area, x_t, y_t = bounderies_detect( img_ )
    files[current_image][3] = area[0]
    files[current_image][4] = area[0]+area[2]
    files[current_image][5] = area[1]
    files[current_image][6] = area[1]+area[3]

    updateMarkers(files[current_image])
    updateSliders() 

def rot_right():
    global rotation

    if(len(files)<1):
        return
    
    rotation -= 90
    if(rotation == 360):
        rotation = 0

    updatePreview(files[current_image], rotation)

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
canvas = Canvas(window, width=1040, height= 845)
a = canvas.create_rectangle(0, 0,  1040, 845, fill='gray')
canvas.move(a, 0, 0)
image_container = canvas.create_image(0,0, anchor="nw")
canvas.place(height=845, width=1040, x=545, y=45)

# markers
x1_bar = canvas.create_line(0, 0, 0, 845, fill="red", width=1)
x2_bar = canvas.create_line(0, 0, 0, 845, fill="red", width=1)
y1_bar = canvas.create_line(0, 0, 1040, 0, fill="red", width=1)
y2_bar = canvas.create_line(0, 0, 1040, 0, fill="red", width=1)

# Apply Button
enable_sliders_butt = Button(window, text = "Apply",command=apply)  
enable_sliders_butt.place(height=30, width=100, x=212, y=200)

#sliders for border adjustments
x1_slider = Scale(window, from_=0, to_=3, label="left", showvalue=0, orient=HORIZONTAL, command=x1_slider_update)
x1_slider.place(width=485, x=20, y=95)

x2_slider = Scale(window, from_=0, to_=3, label="right", showvalue=0, orient=HORIZONTAL, command=x2_slider_update)
x2_slider.place(width=485, x=20, y=140)

y1_slider = Scale(window, from_=0, to_=3, label="top", showvalue=0, orient=HORIZONTAL, command=y1_slider_update)
y1_slider.place(width=485, x=20, y=230)

y2_slider = Scale(window, from_=0, to_=3, label="bottom", showvalue=0, orient=HORIZONTAL, command=y2_slider_update)
y2_slider.place(width=485, x=20, y=275)

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

# position label
pos_cnt = Label(window, text="")
pos_cnt.place(height=15, width=35, x=426, y=80)

window.mainloop()