from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QCheckBox, QGridLayout, QComboBox, QDoubleSpinBox, QTabWidget, QSpacerItem, QSizePolicy, QMessageBox, QStackedWidget
import json
from iobt_options import default_enabled, default_offsets, default_toggles, default_misc, temp_offsets, tooltips_enabled
import psutil
import winreg
import qdarktheme
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Desktop Body Tracking Configurator")
        
        if "vrserver.exe" in (p.name() for p in psutil.process_iter()):
            dlg = QMessageBox()
            dlg.setWindowTitle("Virtual Desktop Body Tracking Configurator")            
            dlg.setText("Error!\n\nvrserver.exe running!\n\nPlease close SteamVR and try again")
            dlg.exec()
            exit()
        
        self.steam = ""
        try:
            location = winreg.HKEY_LOCAL_MACHINE
            path = winreg.OpenKeyEx(location, r"SOFTWARE\Wow6432Node\Valve\Steam")
            self.steam = winreg.QueryValueEx(path, "InstallPath")[0]
            self.steam = self.steam.replace("\\","/")
            if path:
                winreg.CloseKey(path)
        except Exception as e:
            dlg = QMessageBox()
            dlg.setWindowTitle("Virtual Desktop Body Tracking Configurator")            
            dlg.setText(f"Error: {e}")
            dlg.exec()
            exit()
        
        self.ui_elements = {}
        
        layoutTab1 = QGridLayout()
        self.layoutTab2 = QGridLayout()
        self.layoutTab2.setColumnMinimumWidth(1,150)
        layoutTab3 = QVBoxLayout()
        
        for variable in default_toggles:
            button = QCheckBox(variable.replace("_", " ").title())
            button.setCheckable(True)
            button.setChecked(default_toggles.get(variable))
            self.ui_elements[f"misc_{variable}"] = button
            layoutTab3.addWidget(button)
            
        for variable in default_misc:
            box = QDoubleSpinBox()
            box.setPrefix(f"{variable.replace('_', ' ').title()}: ")
            box.setMinimum(0)
            box.setMaximum(1)
            box.setSingleStep(0.05)
            box.setDecimals(3)
            box.setValue(default_misc[variable])
            self.ui_elements[f"misc_{variable}"] = box
            layoutTab3.addWidget(box)      
        
        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        spacer2 = QSpacerItem(100, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        spacer3 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        layoutTab1.addItem(spacer, 16, 0)
        layoutTab1.addItem(spacer3,1,0)
        self.layoutTab2.addItem(spacer2,0, 1)
        
        self.upperWithHip = QPushButton("Upper Body (With Hip)")
        self.upperWithHip.clicked.connect(self.Upper_With_Hip_clicked)
        layoutTab1.addWidget(self.upperWithHip, 0, 0)
        
        self.upper = QPushButton("Upper Body Only")
        self.upper.clicked.connect(self.upper_only_clicked)
        layoutTab1.addWidget(self.upper, 0, 1)
        
        self.elbows = QPushButton("Elbows Only")
        self.elbows.clicked.connect(self.elbows_only_clicked)
        layoutTab1.addWidget(self.elbows, 0, 2)
        
        self.defaults = QPushButton("Reset Enabled Trackers to Defaults")
        self.defaults.clicked.connect(self.reset_clicked)
        layoutTab1.addWidget(self.defaults, 17, 0)
        
        self.load = QPushButton("Load Current Settings")
        self.load.clicked.connect(self.load_settings_clicked)
        layoutTab1.addWidget(self.load, 17, 1)
        
        self.load2 = QPushButton("Load Current Settings")
        self.load2.clicked.connect(self.load_settings_clicked)
        self.layoutTab2.addWidget(self.load2, 4, 0)
        
        self.load3 = QPushButton("Load Current Settings")
        self.load3.clicked.connect(self.load_settings_clicked)
        layoutTab3.addWidget(self.load3)
        
        self.export = QPushButton("Apply Settings (All Pages)")
        self.export.setStyleSheet("QPushButton {background-color: rgb(0,200,0); color: black} QPushButton:hover {background-color: rgb(0,200,150)}")
        self.export.clicked.connect(self.export_clicked)
        layoutTab1.addWidget(self.export, 17, 2)
        
        self.export2 = QPushButton("Apply Settings (All Pages)")
        self.export2.setStyleSheet("QPushButton {background-color: rgb(0,200,0); color: black} QPushButton:hover {background-color: rgb(0,200,150)}")
        self.export2.clicked.connect(self.export_clicked)
        self.layoutTab2.addWidget(self.export2, 5, 0)
        
        self.export3 = QPushButton("Apply Settings (All Pages)")
        self.export3.setStyleSheet("QPushButton {background-color: rgb(0,200,0); color: black} QPushButton:hover {background-color: rgb(0,200,150)}")
        self.export3.clicked.connect(self.export_clicked)
        layoutTab3.addWidget(self.export3, 10)
        
        self.loadRecommended = QCheckBox("Apply Recommended Offsets\n(Does not override custom offsets)")
        self.loadRecommended.setChecked(True)
        self.loadRecommended.clicked.connect(self.checkbox_interacted)
        self.layoutTab2.addWidget(self.loadRecommended, 3, 0)
        
        first = 0
        row = 3
        column = 0
        for variable in default_enabled:
            button = QCheckBox(variable[:-8].replace("_", " ").title())
            button.setCheckable(True)
            button.setChecked(default_enabled.get(variable))
            button.setToolTip(tooltips_enabled[variable])
            button.clicked.connect(lambda checked, b=button: self.checkbox_interacted(b))
            self.ui_elements[f"checkbox_{variable}"] = button
            layoutTab1.addWidget(button, row, column)
            row += 1
            first += 1
            if row >= 16 or first == 7:
                row = 3
                column += 1
                
        widgetTab1 = QWidget()
        widgetTab1.setLayout(layoutTab1)
            
        self.dropdown = QComboBox()
            
        for axis in ["Translate X", "Translate Y", "Translate Z", "Rotate X", "Rotate Y", "Rotate Z"]:
            self.ui_elements[f"stackedwidget_{axis}"] = QStackedWidget()
        
        row = 0
        column = 0
        for variable in default_enabled:        
            self.dropdown.addItem(variable[:-8].replace("_", " ").title())
            
            for axis in ["Translate X", "Translate Y", "Translate Z", "Rotate X", "Rotate Y", "Rotate Z"]:
                box = QDoubleSpinBox()
                box.setPrefix(f"{axis}: ")
                
                if axis[:-2] == "Rotate":
                    box.setMaximum(360)
                    box.setMinimum(-360)
                    box.setSingleStep(90)
                    try:
                        box.setValue(default_offsets[f"{variable[:-8]}_rot_{axis[-1].lower()}"])
                    except:
                        pass
                else:
                    box.setSingleStep(0.01)
                    box.setMaximum(1)
                    box.setMinimum(-1)
                    box.setDecimals(3)                    
                
                self.ui_elements[f"offset_{variable}_{axis}"] = box
                self.ui_elements[f"stackedwidget_{axis}"].addWidget(box)
                row += 1
                
                if row >= 9:
                    row = 0
                    column += 1
        
        self.layoutTab2.addWidget(self.dropdown, 2, 0)
        
        i = 1
        for axis in ["Translate X", "Translate Y", "Translate Z", "Rotate X", "Rotate Y", "Rotate Z"]:
            self.layoutTab2.addWidget(self.ui_elements[f"stackedwidget_{axis}"], i, 2)
            i += 1
        
        self.dropdown.currentIndexChanged.connect(self.offset_index_changed)
        
        widgetTab2 = QWidget()
        widgetTab2.setLayout(self.layoutTab2)
        
        widgetTab3 = QWidget()
        widgetTab3.setLayout(layoutTab3)
        
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setMovable(True)
        tabs.addTab(widgetTab1, "Enabled Trackers")
        tabs.addTab(widgetTab2, "Tracker Offsets")
        tabs.addTab(widgetTab3, "Miscellaneous")
        self.setCentralWidget(tabs)
          
    def offset_index_changed(self, index):
        for axis in ["Translate X", "Translate Y", "Translate Z", "Rotate X", "Rotate Y", "Rotate Z"]:
            self.ui_elements[f"stackedwidget_{axis}"].setCurrentIndex(index)
                
    def checkbox_interacted(self, checkbox):
        pass
     
    def reset_clicked(self):
        for variable, checkbox in self.ui_elements.items():
            if variable.startswith("checkbox_"):
                default_state = default_enabled.get(variable[9:], False)
                checkbox.setChecked(default_state)
        
    def Upper_With_Hip_clicked(self):
        for variable, checkbox in self.ui_elements.items():
            if variable.startswith("checkbox_"):
                if variable[9:] in ["left_arm_upper_joint_enabled", "left_arm_lower_joint_enabled", "right_arm_upper_joint_enabled", "right_arm_lower_joint_enabled", "chest_joint_enabled", "hips_joint_enabled"]:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False) 
    
    def upper_only_clicked(self):
        for variable, checkbox in self.ui_elements.items():
            if variable.startswith("checkbox_"):
                if variable[9:] in ["left_arm_upper_joint_enabled", "left_arm_lower_joint_enabled", "right_arm_upper_joint_enabled", "right_arm_lower_joint_enabled", "chest_joint_enabled"]:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)
        
    def elbows_only_clicked(self):
        for variable, checkbox in self.ui_elements.items():
            if variable.startswith("checkbox_"):
                if variable[9:] in ["left_arm_upper_joint_enabled", "left_arm_lower_joint_enabled", "right_arm_upper_joint_enabled", "right_arm_lower_joint_enabled"]:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False) 
    
    def load_settings_clicked(self):
        try:
            with open(os.path.join(self.steam, "config", "steamvr.vrsettings"), "r") as file:
                current = json.load(file)["driver_VirtualDesktop"]                  
                
                for variable, checkbox in self.ui_elements.items():
                    if variable.startswith("checkbox_"):
                        try:
                            checkbox.setChecked(current[variable[9:]])
                        except:
                            pass
                    
                    if variable.startswith("offset_"):
                        _, joint, axis = variable.split("_")
                        try:                
                            if axis.startswith("Rotate"):
                                checkbox.setValue(current[f"{joint}_rot_{axis[-1].lower()}"])
                            else:
                                checkbox.setValue(current[f"{joint}_offset_{axis[-1].lower()}"])
                        except:
                            pass
                    
                    if variable.startswith("misc_"):
                        try:
                            if isinstance(self.ui_elements[variable], QDoubleSpinBox):
                                self.ui_elements[variable].setValue(current[variable[5:]])
                            else:
                                self.ui_elements[variable].setChecked(current[variable[5:]])
                        except:
                            pass
            
        except Exception as e:
            if str(e) == r"'driver_VirtualDesktop'":
                pass
            else:
                dlg = QMessageBox()
                dlg.setWindowTitle("Virtual Desktop Body Tracking Configurator")            
                dlg.setText(f"Error: {e}")
                dlg.exec()
                exit()
        
    def export_clicked(self):
        export_dict = {}
        if self.loadRecommended.isChecked():
            export_dict.update(temp_offsets)
                
        for variable, checkbox in self.ui_elements.items():
            if variable.startswith("checkbox_"):
                if default_enabled[variable[9:]] != checkbox.isChecked():
                    export_dict[variable[9:]] = checkbox.isChecked()
            
            if variable.startswith("offset_"):
                _, joint, axis = variable.split("_")
                if axis.startswith("Rotate"):
                    try:
                        if abs(checkbox.value() - default_offsets[f"{joint}_rot_{axis[-1].lower()}"]) >= 0.001:
                            export_dict[f"{joint}_rot_{axis[-1].lower()}"] = checkbox.value()
                    except:
                        if checkbox.value() >= 0.001:
                            export_dict[f"{joint}_rot_{axis[-1].lower()}"] = checkbox.value()
                else:
                    try:
                        if abs(checkbox.value() - default_offsets[f"{joint}_offset_{axis[-1].lower()}"]) >= 0.001:
                            export_dict[f"{joint}_offset_{axis[-1].lower()}"] = checkbox.value()
                    except:
                        if checkbox.value() >= 0.001:
                            export_dict[f"{joint}_offset_{axis[-1].lower()}"] = checkbox.value()
            
            if variable.startswith("misc_"):
                try:
                    if abs(default_misc[variable[5:]] - self.ui_elements[variable].value()) >= 0.001:
                        export_dict[variable[5:]] = self.ui_elements[variable].value()
                except:
                    if default_toggles[variable[5:]] != self.ui_elements[variable].isChecked():
                        export_dict[variable[5:]] = self.ui_elements[variable].isChecked()
           
        try:   
            with open(os.path.join(self.steam, "config", "steamvr.vrsettings"), "r+") as settings:
                temp = json.load(settings)
                
                backup_original_path = os.path.join(self.steam, "config", "steamvr.vrsettings.originalbackup")
                backup_last_path = os.path.join(self.steam, "config", "steamvr.vrsettings.lastbackup")
                
                if not os.path.exists(backup_original_path):
                    with open(backup_original_path, "w") as backup:
                        json.dump(temp, fp=backup)
                
                with open(backup_last_path, "w") as backup:
                    json.dump(temp, fp=backup)
                
                temp["driver_VirtualDesktop"] = export_dict
                settings.seek(0)
                json.dump(temp, indent=3, fp=settings)
                settings.truncate()
                
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Virtual Desktop Body Tracking Configurator")            
                dlg.setText(f"Successfully exported to SteamVR!\n\nBackup of original is saved at: {backup_original_path}\n\nAnd backup of previous settings is saved at: {backup_last_path}")
                dlg.exec()
                app.exit()
        
        except Exception as e:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Virtual Desktop Body Tracking Configurator")            
            dlg.setText(f"Error: {e}")
            dlg.exec()
            app.exit()
            
app = QApplication([])
qdarktheme.setup_theme(additional_qss="QToolTip { border: 0px; }")
window = MainWindow()
window.show()
app.exec()