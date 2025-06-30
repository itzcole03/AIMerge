from PIL import Image

# Load the screenshot
img = Image.open('screennshot.png')

# Define crop boxes (left, upper, right, lower)
# These coordinates may need adjustment based on actual button positions
accept_box = (280, 660, 360, 700)  # (left, upper, right, lower)
reject_box = (200, 660, 280, 700)

# Crop and save Accept button
accept_img = img.crop(accept_box)
accept_img.save('accept.png')

# Crop and save Reject button
reject_img = img.crop(reject_box)
reject_img.save('reject.png')

print('Cropped accept.png and reject.png successfully.') 