call ./palworld_breeding_tree\Scripts\activate.bat
pyinstaller --onefile --clean ^
--noconsole ^
--distpath "../Build" ^
--specpath "../.Building" ^
--name "Palworld Breeding Tree - 3.0.0 - Windows" ^
--icon "../Source/Icons/icon.ico" ^
--workpath "../.Building" ^
--collect-all graphviz ^
--hidden-import="graphviz._defaults" ^
--hidden-import="graphviz.backend" ^
--hidden-import="graphviz.dot" ^
--add-data "C:\Users\mazin.DESKTOP-RCQGMS8\Documents\projets_dev\Palworld_Breeding_Tree\Source\Graphviz;Graphviz" ^
--add-data "C:\Users\mazin.DESKTOP-RCQGMS8\Documents\projets_dev\Palworld_Breeding_Tree\Source\languages;languages" ^
--add-data "C:\Users\mazin.DESKTOP-RCQGMS8\Documents\projets_dev\Palworld_Breeding_Tree\Source\Icons;Icons" ^
--add-data "C:\Users\mazin.DESKTOP-RCQGMS8\Documents\projets_dev\Palworld_Breeding_Tree\Source\pals.json;." ^
main.py
