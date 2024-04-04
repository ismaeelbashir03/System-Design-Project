def parsePgm(path):
    with open(path, "rb") as file:
        lines = file.readlines()
        assert lines[0] == b"P5\n"
        width, height = [int(i.decode()) for i in lines[2].strip().split()]
        depth = int(lines[3].decode())
        data = [int(i) for i in lines[4]]
        data = [data[i:i+width] for i in range(0, len(data), width)]

        # Trying to pretty up the map
        import matplotlib.pyplot as plt
        # width, height, depth, data = (parsePgm("maps/map.pgm"))
        data2 = data.copy()
        for x in range(3):
            for i in range(len(data) - 2):
                for j in range(len(data[i]) - 2):
                    if (i > 0 and j > 0):
                        count = 0
                        countFive = 0
                        countFour = 0
                        countZero = 0
                        for k in range (-1, 2):
                            for z in range (-1, 2):
                                if (not data[i][j] == 254 and (z != 0 or k != 0) and data[i+z][j+k] == 254):
                                    countFour += 1
                                if (not data[i][j] == 205 and (z != 0 or k != 0) and data[i+z][j+k] == 205):
                                    countFive += 1
                                if (not data[i][j] == 0 and (z != 0 or k != 0) and data[i+z][j+k] == 0):
                                    countZero += 1
                                if(data[i][j] == 0 and (k != 0 or z != 0) and data[i+z][j+k] == 0):
                                    count+=1
                        if (count < 2 and data[i][j] == 0):
                            data2[i][j] = 205
                        if (countZero > 4):
                            data2[i][j] = 0
                        if (countFive >= 5 and not countFour >= 5):
                            data2[i][j] = 205
                        elif (countFour >= 6):
                            data2[i][j] = 254
            data = data2.copy()

        return width, height, depth, data
