# -*- coding:utf-8 -*-
import os
import sys
import glob

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from classify import FlowerClassifier

QTextCodec.setCodecForTr(QTextCodec.codecForName('utf8'))


class MainDialog(QDialog):
    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        self.classifier = FlowerClassifier()
        self.file_good = open('good_image.txt', 'a')
        self.file_bad = open('bad_image.txt', 'a')
        self.file_unknown = open('unknown_image.txt', 'a')

        self.setWindowTitle(self.tr("图像打标工具"))
        self.setFixedSize(QSize(650, 450))

        self.current_non_label_image_path = ''
        self.current_reference_image_path = ''
        self.auto_image_path = ''
        self.auto_images = []
        self.all_images = []
        self.image_index = 0
        self.num_of_image = 0

        # show image label
        self.reference_image = QLabel()
        self.non_label_image = QLabel()

        radio_button_manual = QRadioButton(self.tr("手动"))
        radio_button_auto = QRadioButton(self.tr("自动"))
        radio_button_manual.setChecked(True)

        self.imageLabelQLabel = QLineEdit()
        self.current_path = QLabel()
        self.info_text = QTextEdit()

        # manual layout
        manual_layout_h_ = QHBoxLayout()
        self.manual_layout_reference_image = QPushButton(self.tr("参考图像"))
        self.manual_layout_non_label_image = QPushButton(self.tr("待识别图像"))
        manual_layout_h_.addWidget(self.manual_layout_reference_image)
        manual_layout_h_.addWidget(self.manual_layout_non_label_image)

        manual_layout_h = QHBoxLayout()
        self.manual_layout_line_edit = QLineEdit()
        self.manual_layout_line_edit_reference = QLineEdit()
        self.manual_layout_line_edit_reference.setEnabled(False)
        manual_layout_h.addWidget(QLabel(self.tr("参考标签")))
        manual_layout_h.addWidget(self.manual_layout_line_edit_reference)
        manual_layout_h.addWidget(QLabel(self.tr("标签")))
        manual_layout_h.addWidget(self.manual_layout_line_edit)

        self.manual_layout_previous_image = QPushButton(self.tr("上一张"))
        self.manual_layout_next_image = QPushButton(self.tr("下一张"))
        manual_layout_h_image_button = QHBoxLayout()
        manual_layout_h_image_button.addWidget(self.manual_layout_previous_image)
        manual_layout_h_image_button.addWidget(self.manual_layout_next_image)
        manual_layout = QVBoxLayout()
        manual_layout.addLayout(manual_layout_h_)
        manual_layout.addLayout(manual_layout_h)
        manual_layout.addLayout(manual_layout_h_image_button)

        # auto layout
        auto_layout = QVBoxLayout()
        self.auto_info_text = QTextEdit()
        self.set_path_button = QPushButton(self.tr("选择路径"))
        self.recognize_button = QPushButton(self.tr("识别"))
        auto_layout_button_h = QHBoxLayout()
        auto_layout_button_h.addWidget(self.set_path_button)
        auto_layout_button_h.addWidget(self.recognize_button)
        auto_layout.addWidget(self.auto_info_text)
        auto_layout.addLayout(auto_layout_button_h)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.reference_image, 0, 0)
        grid_layout.addWidget(self.non_label_image, 0, 1)
        grid_layout.addWidget(radio_button_auto, 1, 0)
        grid_layout.addWidget(radio_button_manual, 1, 1)
        grid_layout.addLayout(auto_layout, 2, 0)
        grid_layout.addLayout(manual_layout, 2, 1)

        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(grid_layout)
        # vertical_layout.addLayout(current_path_layout)
        vertical_layout.addWidget(self.current_path)
        vertical_layout.addWidget(self.info_text)

        self.setLayout(vertical_layout)
        self.set_init_image()

        # connect signal slot
        # self.connect(open_image_button, SIGNAL("clicked()"), self.open_file)
        self.connect(self.manual_layout_reference_image, SIGNAL("clicked()"), self.set_reference_image)
        self.connect(self.manual_layout_non_label_image, SIGNAL("clicked()"), self.set_image)
        self.connect(self.manual_layout_previous_image, SIGNAL("clicked()"), self.open_previous_image)
        self.connect(self.manual_layout_next_image, SIGNAL("clicked()"), self.open_next_image)
        self.connect(self.recognize_button, SIGNAL("clicked()"), self.auto_label)
        self.connect(self.set_path_button, SIGNAL("clicked()"), self.set_auto_path)
        self.classifier.result_signal.connect(self.show_result)
        self.classifier.image_path_signal.connect(self.show_image)

    def set_init_image(self, reference_image_path=None, image_path=None):
        if reference_image_path is None:
            reference_image_path = "/home/yanlei/Pictures/1a_Anthurium-hookeri.jpg"
        else:
            reference_image_path = reference_image_path
        if image_path is None:
            image_path = "/home/yanlei/Pictures/2_02e8a61987e89aac8f69fc000a0de7c1.png"
        else:
            image_path = image_path
        self.show_reference_image(reference_image_path)
        self.show_image(image_path)

    def show_reference_image(self, reference_image_path):
        # fixed image size
        if reference_image_path is not None:
            image_fixed_size = QSize(320, 200)
            picture = QPixmap()
            picture.load(reference_image_path)
            self.reference_image.setPixmap(picture.scaled(image_fixed_size))

    def show_image(self, image_path):
        if image_path is not None:
            self.set_current_path_info(image_path)
            image_fixed_size = QSize(320, 200)
            picture = QPixmap()
            picture.load(image_path)
            self.non_label_image.setPixmap(picture.scaled(image_fixed_size))

    def open_file(self):
        s = QFileDialog.getOpenFileName(self, self.tr("选择文件"), "/home", "*.*")
        self.current_path.setText(str(s))
        self.set_info(str(s))

    def set_reference_image(self):
        s = QFileDialog.getOpenFileName(self, self.tr("选择图像文件"), "/home", "*.*")
        if s:
            self.current_reference_image_path = str(s)
            self.show_reference_image(reference_image_path=str(s))
        else:
            self.set_init_image()

    def set_image(self):
        s = QFileDialog.getOpenFileName(self, self.tr("选择图像文件"), "/home", "*.*")
        if s:
            self.current_non_label_image_path = str(s)
            path = os.path.split(self.current_non_label_image_path)[0]
            self.all_images = glob.glob(path + '/*.*')
            self.num_of_image = len(self.all_images)
            self.image_index = 0
            self.show_image(image_path=str(s))
        else:
            self.set_init_image()

    def open_previous_image(self):
        if 0 <= self.image_index <= self.num_of_image:
            if self.image_index is self.num_of_image:
                self.image_index -= 1
            path = self.all_images[self.image_index]
            self.set_current_path_info(path)
            if self.image_index is not 0:
                self.image_index -= 1
            self.show_image(path)

    def open_next_image(self):
        if 0 <= self.image_index < self.num_of_image:
            path = self.all_images[self.image_index]
            self.set_current_path_info(path)
            self.image_index += 1
            self.show_image(path)

    def auto_label(self):
        self.classifier.set_image(self.auto_images)
        self.classifier.start()

    def set_auto_path(self):
        s = QFileDialog.getExistingDirectory(self, self.tr("选择图像文件夹"), "/home")
        self.auto_image_path = str(s)
        self.auto_images = glob.glob(self.auto_image_path + '/*/*.jpg')
        self.auto_images.extend(glob.glob(self.auto_image_path + '/*/*.JPG'))
        self.auto_images.extend(glob.glob(self.auto_image_path + '/*/*.png'))
        self.auto_images.extend(glob.glob(self.auto_image_path + '/*/*.PNG'))

    def set_info(self, info):
        self.info_text.append(info)

    def set_auto_info(self, info):
        self.auto_info_text.clear()
        self.auto_info_text.setText(info)

    def set_current_path_info(self, text):
        self.current_path.setText(self.tr("当前图片：") + text)

    def show_result(self, results):
        image_path = results['image_path']
        result = results['result']
        time = results['time']
        prob = result[0]['prob']
        label = result[0]['label']
        line = image_path + ' ' + label + '\n'
        if prob > 0.9:
            self.file_good.write(line)
        elif prob < 0.6:
            self.file_bad.write(line)
        else:
            self.file_unknown.write(line)

        result_str = "Label:{0}\nProb:{1}\nTime:{2} ms".format(result[0]['label'], result[0]['prob'], str(time))
        self.set_auto_info(result_str)
        self.set_info(result_str)


app = QApplication(sys.argv)
dialog = MainDialog()
dialog.show()
app.exec_()
