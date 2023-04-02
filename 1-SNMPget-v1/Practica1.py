import PySimpleGUI as sg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from os import remove, path, rename, listdir
from pysnmp.hlapi import *
import itertools


w, h = letter


def getinfo(oid, ipaddress="localhost", puerto=161, comunidad="comunidadSNMP"):
    resp = ""
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(comunidad, mpModel=0),
        UdpTransportTarget((ipaddress, puerto)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    errorindication, errorstatus, errorindex, varbinds = next(iterator)

    if errorindication:
        print(errorindication)

    elif errorstatus:
        print('%s at %s' % (errorstatus.prettyPrint(), errorindex and varbinds[int(errorindex) - 1][0] or '?'))

    else:
        for varBind in varbinds:
            resp = (' = '.join([x.prettyPrint() for x in varBind]))
            resp = resp.split()[2]
            if resp == 'Hardware:':
                resp = (' = '.join([x.prettyPrint() for x in varBind]))
                resp = resp.split()[14]
                #resp =hex_to_string(resp)
    return resp


def hex_to_string(hexadecimal):
    new = ""
    if hexadecimal[:2] == '0x':
        new = hexadecimal[2:]
    string_value = bytes.fromhex(new).decode('utf-8')
    return string_value


def grouper(iterable, n):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args)


def export_to_pdf(data, c):
    c.setFont("Times-Roman", 16)
    c.drawString(65, h - 325, "Informacion de interfaces:")
    c.setFont("Times-Roman", 12)
    max_rows_per_page = 25
    # Margin.
    x_offset = 50
    y_offset = 350
    # Space between rows.
    padding = 25

    xlist = [x + x_offset for x in [0, 350, 350, 500]]
    ylist = [h - y_offset - i * padding for i in range(max_rows_per_page + 1)]

    for rows in grouper(data, max_rows_per_page):
        rows = tuple(filter(bool, rows))
        c.grid(xlist, ylist[:len(rows) + 1])
        for y, row in zip(ylist[:-1], rows):
            for x, cell in zip(xlist, row):
                if len(str(cell)) > 60:
                    c.drawString(x + 2, y - padding + 3, str(cell)[0:40] + "...")
                else:
                    c.drawString(x + 2, y - padding + 3, str(cell))
        c.showPage()

    c.save()


def menu():
    layout = [
        [sg.Text("Sistema de Administracion de Red", font="Times-Roman 14 bold", text_color="#000",
                 justification="center", background_color="#fff")],
        [sg.Text("Practica 1 - Adquisicion de Informacion", font="Times-Roman 14 bold", text_color="#000",
                 justification="center", background_color="#fff")],
        [sg.Text("Becerra Ramirez Luis Arturo 4CM14 2019630196", font="Times-Roman 14 bold", text_color="#000",
                 justification="center", background_color="#fff")],
        [sg.Text("Elige una opcion: ", font="Times-Roman 12", text_color="#000",
                 justification="left", background_color="#fff"), sg.InputText(background_color="#fff", border_width=0)],
        [sg.Text("1) Agregar dispositivo", font="Times-Roman 12", text_color="#000",
                 justification="left", background_color="#fff")],
        [sg.Text("2) Cambiar informacion de dispositivo", font="Times-Roman 12", text_color="#000",
                 justification="left", background_color="#fff")],
        [sg.Text("3) Eliminar dispositivo", font="Times-Roman 12", text_color="#000",
                 justification="left", background_color="#fff")],
        [sg.Text("4) Listar dispositivo", font="Times-Roman 12", text_color="#000",
                 justification="left", background_color="#fff")],
        [sg.Button("Aceptar")]
    ]

    window = sg.Window("Inicio", layout, margins=(80, 80), background_color="#fff")
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            window.close()
            break
        if event == "Aceptar":
            if values[0] == "1":
                window.close()
                layout1 = [
                    [sg.Text("Comunidad:    ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0)],
                    [sg.Text("Version SNMP:    ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0)],
                    [sg.Text("Puerto:       ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0)],
                    [sg.Text("IP:       ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0)],
                    [sg.Button("Guardar")],
                    [sg.Button("Cancelar")]
                ]

                window1 = sg.Window("Agregar dispositivo", layout1, margins=(80, 80), background_color="#fff")
                while True:
                    event1, values1 = window1.read()
                    if event1 == "Exit" or event1 == sg.WIN_CLOSED:
                        window1.close()
                        break
                    if event1 == "Guardar":
                        try:
                            file = open(values1[3] + "-" + values1[2] + ".txt", "w+")
                            file.write(values1[0] + "\n" + values1[1] + "\n" + values1[2] + "\n" + values1[3])
                            file.close()
                            print("Dispositivo guardado")
                            window1.close()
                            menu()
                        except OSError as err:
                            print("Error: {0}".format(err))
                    if event1 == "Cancelar":
                        window1.close()
                        menu()
                    else:
                        window1.close()
                        break
            if values[0] == "3":
                window.close()
                layout2 = [
                    [sg.Text("Puerto:       ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0)],
                    [sg.Text("IP:           ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0)],
                    [sg.Button("Eliminar")],
                    [sg.Button("Cancelar")]
                ]

                window2 = sg.Window("Eliminar dispositivo", layout2, margins=(80, 80), background_color="#fff")
                while True:
                    event2, values2 = window2.read()
                    if event2 == "Exit" or event2 == sg.WIN_CLOSED:
                        window2.close()
                        break
                    if event2 == "Eliminar":
                        try:
                            if path.exists(values2[1] + "-" + values2[0] + ".txt"):
                                remove(values2[1] + "-" + values2[0] + ".txt")
                                print("Dispositivo eliminado")
                            else:
                                print("Archivo no encontrado")
                            window2.close()
                            menu()
                        except OSError as err:
                            print("Error: {0}".format(err))
                    if event2 == "Cancelar":
                        window2.close()
                        menu()
                    else:
                        window2.close()
                        break
            if values[0] == "2":
                window.close()
                contenido = ""
                layout3 = [
                    [sg.Text("Puerto:       ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0)],
                    [sg.Text("IP:           ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0)],
                    [sg.Button("Buscar")]
                ]

                window3 = sg.Window("Buscar dispositivo", layout3, margins=(80, 80), background_color="#fff")
                while True:
                    event3, values3 = window3.read()
                    if event3 == "Exit" or event3 == sg.WIN_CLOSED:
                        window3.close()
                        break
                    if event3 == "Buscar":
                        try:
                            file = open(values3[1] + "-" + values3[0] + ".txt", "r+")
                            contenido = file.read()
                            file.close()
                            window3.close()
                        except OSError as err:
                            print("Error: {0}".format(err))
                    else:
                        break
                info = contenido.split("\n")
                layout4 = [
                    [sg.Text("Comunidad:        ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0, default_text=info[0])],
                    [sg.Text("Version SNMP:     ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0, default_text=info[1])],
                    [sg.Text("Puerto:           ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0, default_text=info[2])],
                    [sg.Text("IP:               ", font="Times-Roman 12", text_color="#000",
                             justification="left", background_color="#fff"),
                     sg.InputText(background_color="#fff", border_width=0, default_text=info[3])],
                    [sg.Button("Actualizar")],
                    [sg.Button("Cancelar")]
                ]

                window4 = sg.Window("Modificar dispositivo", layout4, margins=(80, 80), background_color="#fff")
                while True:
                    event4, values4 = window4.read()
                    if event4 == "Exit" or event4 == sg.WIN_CLOSED:
                        window4.close()
                        break
                    if event4 == "Actualizar":
                        try:
                            file = open(values4[3] + "-" + values4[2] + ".txt", "w+")
                            file.write(values4[0] + "\n" + values4[1] + "\n" + values4[2] + "\n" + values4[3])
                            file.close()
                            if path.exists(info[3] + "-" + info[2] + ".txt"):
                                rename(info[3] + "-" + info[2] + ".txt", values4[3] + "-" + values4[2] + ".txt")
                            print("Dispositivo modificado")
                            window4.close()
                            menu()
                        except OSError as err:
                            print("Error: {0}".format(err))
                    if event4 == "Cancelar":
                        window4.close()
                        menu()
                    else:
                        window4.close()
                        break
            if values[0] == "4":
                window.close()
                file_list = listdir("./")
                names = [
                    f
                    for f in file_list
                    if path.isfile(path.join("./", f)) and f.lower().endswith(".txt")
                ]
                layout5 = [
                    [sg.Listbox(values=names, enable_events=True, size=(30, 20), font="Times-Roman 12",
                                text_color="#000", background_color="#fff", key="-List-")
                     ],
                    [sg.Button("Generar reporte")]
                ]

                window5 = sg.Window("Generar reporte", layout5, margins=(80, 80), background_color="#fff")
                while True:
                    event5, values5 = window5.read()
                    if event5 == "Exit" or event5 == sg.WIN_CLOSED:
                        window5.close()
                        break
                    if event5 == "Generar reporte":
                        if len(values5["-List-"]) != 1:
                            print("Debes seleccionar un archivo solamente")
                        else:
                            content = ""
                            data = str.split(values5["-List-"][0][0:-4], "-")
                            try:
                                device = open(data[0] + "-" + data[1] + ".txt", "r+")
                                content = device.read()
                                device.close()
                            except OSError as err:
                                print("Error: {0}".format(err))

                            infodata = content.split("\n")

                            c = canvas.Canvas("Reporte-De-Agente-LABR.pdf", pagesize=letter)

                            data = [("Interfaz", "Estatus Administrativo")]

                            res = getinfo(ObjectIdentity('1.3.6.1.2.1.1.1.0'), infodata[3],
                                          int(infodata[2]), infodata[0])
                            sysOp = res
                            res = getinfo(ObjectIdentity('1.3.6.1.2.1.1.4.0'), infodata[3],
                                          int(infodata[2]), infodata[0])
                            contact = res
                            res = getinfo(ObjectIdentity('1.3.6.1.2.1.1.5.0'), infodata[3],
                                          int(infodata[2]), infodata[0])
                            eqName = res
                            res = getinfo(ObjectIdentity('1.3.6.1.2.1.1.6.0'), infodata[3],
                                          int(infodata[2]), infodata[0])
                            comunity = res
                            res = getinfo(ObjectIdentity('1.3.6.1.2.1.2.1.0'), infodata[3],
                                          int(infodata[2]), infodata[0])
                            num = res

                            c.setFont("Times-Roman", 16)
                            c.drawString(50, h - 75, "Administracion de Servicios en Red")
                            c.drawString(50, h - 100, "Practica 1: Adquisicion de informacion usando SNMP")
                            c.drawString(50, h - 125, "Becerra Ramirez Luis Arturo 4CM14")

                            c.setFont("Times-Roman", 16)
                            c.drawString(65, h - 175, "Informacion del Agente")

                            c.setFont("Times-Roman", 14)
                            c.drawString(80, h - 200, "Sistema operativo: " + sysOp)
                            if sysOp.__contains__("Windows"):
                                c.drawImage("Windows.png", (w / 2) + 150, h - 175, width=50, height=50)
                            if sysOp.__contains__("Linux"):
                                c.drawImage("Linux.png", (w / 2) + 150, h - 175, width=50, height=50)
                            if sysOp.__contains__("Mac"):
                                c.drawImage("Mac.png", (w / 2) + 150, h - 175, width=50, height=50)
                            if sysOp.__contains__("Ubuntu"):
                                c.drawImage("Ubuntu.png", (w / 2) + 150, h - 175, width=50, height=50)

                            c.drawString(80, h - 225, "Nombre del dispositivo: " + eqName)
                            c.drawString(80, h - 250, "Informacion del contacto: " + contact)
                            c.drawString(80, h - 275, "Ubicacion: " + comunity)
                            c.drawString(80, h - 300, "Numero de interfaces: " + num)


                            for i in range(1, int(6)):
                                res = getinfo(ObjectIdentity('1.3.6.1.2.1.2.2.1.7.' + str(i)), infodata[3],
                                              int(infodata[2]), infodata[0])
                                stA = res
                                if stA == "1":
                                    stA = "Up"
                                elif stA == "2":
                                    stA = "Down"
                                else:
                                    stA = "Testing"
                                res = getinfo(ObjectIdentity('1.3.6.1.2.1.2.2.1.2.' + str(i)), infodata[3],
                                              int(infodata[2]), infodata[0])
                                if sysOp.__contains__("Windows"):
                                    name = hex_to_string(res)
                                elif sysOp.__contains__("Ubuntu"):
                                    name = res
                                elif sysOp.__contains__("Linux"):
                                    name = res
                                elif sysOp.__contains__("Mac"):
                                    name = res
                                data.append((name, stA))

                            export_to_pdf(data, c)
                        window5.close()
                        menu()




menu()
