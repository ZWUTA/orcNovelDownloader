import cv2

img = cv2.imread("./Test/1684742444485.jpg")
print(img.shape)
cropped = img[170:2360, 50:1000]  # 裁剪坐标为[y0:y1, x0:x1]
cv2.imwrite("./cut/cv_cut_thor.jpg", cropped)
