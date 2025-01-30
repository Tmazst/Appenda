
import os
import secrets
from flask import flash

class ImageProcessor:

    ALLOWED_EXTENSIONS = {"txt", "xlxs",'docx', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    def __init__(self,image):

        self.file = image
        print("Checking Image: ",self.file)
        _img_name, _ext = os.path.splitext(self.file.filename)
        print("Checking Image2: ",_img_name)
        gen_random = secrets.token_hex(8)
        new_file_name = gen_random + _ext
        print("Checking Image3: ",new_file_name)

        if self.file.filename == '':
            print("Checking Image4: ",self.file.filename)
            return 'No selected file'

        if self.file.filename:
            print("Checking Image5: ",os.path.join("static\images",new_file_name))
            self.file.save(os.path.join("static\images",new_file_name))
            # flash(f"File Upload Successful!!", "success")
            print("Checking Image6: ",os.path.join("static\images",new_file_name) )
            return new_file_name


    # Processing image files save to db and server
    # def process_file(file):

    #         # filename = secure_filename(file)

    #         _img_name, _ext = os.path.splitext(file.filename)
    #         gen_random = secrets.token_hex(8)
    #         new_file_name = gen_random + _ext

    #         if file.filename == '':
    #             return 'No selected file'

    #         if file.filename and allowed_files(file):
    #             file_saved = file.save(os.path.join(app.config["UPLOADED"],new_file_name))
    #             flash(f"File Upload Successful!!", "success")
    #             return new_file_name

    #         else:
    #             return f"Allowed are [.txt, .xls,.docx, .pdf, .png, .jpg, .jpeg, .gif] only"