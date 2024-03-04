class PrintInformation:
    _goback = "\033[F" 
    _length = 90
    
    #max 10 elements
    _lines = []
    _lines_count = 0

    def print_on_current_line(self, text=''):
        if self._lines_count > 0:
            print(f'{self._goback}{str.ljust(text, self._length)}')

            lines = text.split('\n')
            self._lines_count += len(lines) - 1

            for i, line in enumerate(lines):
                if i > 0:
                    self._add_line(line)
                else:
                    self._lines[-1] = line
        else:
            self.print_new_line(text)

    def print_new_line(self, text=''):
        print(str.ljust(text, self._length))

        lines = text.split('\n')
        self._lines_count += len(lines)

        for line in lines:
            self._add_line(line)
        
    def jump_line(self, lines_count=1):
        if lines_count > self._lines_count:
            print(f'{self._goback*self._lines_count}', end='')
            self._lines_count = 0
            self._lines = []
        else:
            print(f'{self._goback*lines_count}', end='')
            self._lines_count -= lines_count
            del self._lines[-lines_count:]

    def _add_line(self, line):
        if len(self._lines) < 10:
            self._lines.append(line)
        else:
            self._lines.pop(0)
            self._lines.append(line)

    def get_lines_count(self):
        return self._lines_count
    
    def get_lines(self):
        return self._lines
    
    def print_testing_start(self, device_name):
        self.print_on_current_line(f'Testing {device_name} device')
        self.print_new_line()
        self.print_new_line()