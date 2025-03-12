

class UniversalMachine():
    def __init__(self, sp: int, sw: int, maxint: int, max_memory_alloc: int):
        self.sp = sp
        self.sw = sw
        self.maxint = maxint    # contents of cells are in range [-maxint, maxint]
        self.max_memory_alloc = max_memory_alloc   # maximum number of address which can be allocated or freed at a time
        
        self.program_tape = None  # read/execute
        self.work_tape = None     # read/write/execute
        self.output_tape = []   # used used to manipulate external environment
        self.input_tape = []    # used for receiving information from external environment

        self.instruction_pointer = 0
        self.oracle_address = 0
        self.Min = None            # smallest address (-sw <= Min <= 0)
        self.Max = None            # topmost address of the used storage (-1 <= Max <= sp)
        self.current_runtime = 0
        self.max_time_limit = 2**24
        self.current_time_limit = self.max_time_limit

        self.instr_set_lookup_table = [
            "Jumpleq",       # If Value in Address 1 <= Value in Address 2, Jump to Address 3
            "Ouput",         # Write the contents of Address 1 to output
            "Jump",          # Jump to Address 1
            "Stop",          # Halt
            "Add",           # The sum of contents of Address 1 and Address 2 is written to Address 3
            "GetInput",      # Get the (Address 1)-th value of input and write to Address 2
            "Move",          # Copy contents of Address 1 to Address 2
            "Allocate",      # Allocate (Content 1) new memory addresses
            "Increment",     # (Address 1) + 1
            "Decrement",     # (Address 1) - 1
            "Subtract",      # The subtraction of Address 1 from Address 2 is written to Address 3
            "Multiply",      # The product of contents of Address 1 and Address 2 is written to Address 3
            "Free"           # Free / Deallocate (Content 1) memory addresses
        ]

        self.instr_arg_lookup_table = [
            3,
            1,
            1,
            0,
            3,
            2,
            2,
            1,
            1,
            1,
            3,
            3,
            1
        ]

    def run(self, max_steps=None):
        HALT = False
        self.instruction_pointer = 0

        if len(self.program_tape) == 0:
            HALT = True

        step = 0
        while not HALT:
            instruction = self.program_tape[self.instruction_pointer]
            HALT = self.execute_instruction(instruction)
            if step == max_steps:
                print("Maximum time steps reached!")
                HALT = True
            step += 1

        print("Universal Machine halted!")


    def execute_instruction(self, instruction:int):
        HALT = False
        ADDRESSES_VALID = True
        
        tape = self.program_tape + self.work_tape
        num_args = self.instr_arg_lookup_table[instruction]

        if num_args > 0:
            args = self.program_tape[self.instruction_pointer+1:self.instruction_pointer+1+num_args]    # args contains addresses
            ## Check if addresses are in the valid range, defined by Min/Max ##
            if False in [self.is_address_valid(address) for address in args]:
                HALT = True
                ADDRESSES_VALID = False
        else:
            args = None

        if ADDRESSES_VALID:

            if instruction == 0:    
                ###########
                # Jumpleq #
                ###########

                if tape[args[0]] <= tape[args[1]]:
                    self.instruction_pointer = args[2]
                else:
                    self.instruction_pointer += num_args+1

            elif instruction == 1:  
                #########
                # Ouput #
                #########

                self.output_tape.append(tape[args[0]])
                self.instruction_pointer += num_args+1

            elif instruction == 2:  
                ########
                # Jump #
                ########

                self.instruction_pointer = args[0]

            elif instruction == 3:  
                ########
                # Stop #
                ########

                HALT = True

            elif instruction == 4:  
                #######
                # Add #
                #######

                if args[2] > -1:  # we are not allowed to write onto the program tape
                    HALT = True
                else:
                    self.work_tape[args[2]] = tape[args[0]] + tape[args[1]]
                    self.instruction_pointer += num_args+1

            elif instruction == 5:  
                ############
                # GetInput #
                ############

                if args[1] > -1:  # we are not allowed to write onto the program tape
                    HALT = True
                elif (tape[args[0]] >= len(self.input_tape)) or (tape[args[0]] < 0): # check if index of input tape is valid
                    HALT = True
                else:
                    self.work_tape[args[1]] = self.correct_overflow(self.input_tape[tape[args[0]]])
                    self.instruction_pointer += num_args+1

            elif instruction == 6:  
                ########
                # Move #
                ########

                if args[1] > -1:  # we are not allowed to write onto the program tape
                    HALT = True
                else:
                    self.work_tape[args[1]] = tape[args[0]]
                    self.instruction_pointer += num_args+1

            elif instruction == 7:  
                ############
                # Allocate #
                ############

                if ((tape[args[0]] + len(self.work_tape)) > self.sw) or (tape[args[0]] > self.max_memory_alloc):
                    HALT = True
                else:
                    self.work_tape = [0 for _ in range(tape[args[0]])] + self.work_tape
                    self.Min = -len(self.work_tape)
                    self.instruction_pointer += num_args+1

            elif instruction == 8:  
                #############
                # Increment #
                #############

                if args[0] > -1:  # we are not allowed to write onto the program tape
                    HALT = True
                else:
                    self.work_tape[args[0]] += 1
                    self.instruction_pointer += num_args+1

            elif instruction == 9:  
                #############
                # Decrement #
                #############

                if args[0] > -1:  # we are not allowed to write onto the program tape
                    HALT = True
                else:
                    self.work_tape[args[0]] -= 1
                    self.instruction_pointer += num_args+1

            elif instruction == 10: 
                ############
                # Subtract #
                ############

                if args[2] > -1:  # we are not allowed to write onto the program tape
                    HALT = True
                else:
                    self.work_tape[args[2]] = tape[args[1]] - tape[args[0]]
                    self.instruction_pointer += num_args+1

            elif instruction == 11: 
                ############
                # Multiply #
                ############

                if args[2] > -1:  # we are not allowed to write onto the program tape
                    HALT = True
                else:
                    self.work_tape[args[2]] = tape[args[0]] * tape[args[1]]
                    self.instruction_pointer += num_args+1

            elif instruction == 12: 
                ########
                # Free #
                ########
                
                if (tape[args[0]] > self.max_memory_alloc) or (tape[args[0]] > len(self.work_tape)):
                        HALT = True
                else:
                    self.work_tape = self.work_tape[tape[args[0]]:]
                    self.Min = -len(self.work_tape)
                    self.instruction_pointer += num_args+1

            else:
                raise Exception("Invalid Instruction!")
        
        return HALT
    
    def init_program_tape(self, program_tape: list):
        if len(program_tape) <= (self.sp+1):
            self.program_tape = [self.correct_overflow(cell_content)for cell_content in program_tape]   # capping cell content to be in range [-maxint, maxint]
            self.Max = len(program_tape)
        else:
            raise Exception("Program Tape could not be loaded! Program Tape exceeds pre-allocated memory!")

    def init_work_tape(self, work_tape: list):
        if len(work_tape) <= (self.sw+1):
            self.work_tape = [self.correct_overflow(cell_content)for cell_content in work_tape]   # capping cell content to be in range [-maxint, maxint]
            self.Min = -len(work_tape)
        else:
            raise Exception("Work Tape could not be loaded! Work Tape exceeds pre-allocated memory!")

    def init_input_tape(self, input_tape: list):
        self.input_tape = input_tape

    def is_address_valid(self, address: int):
        if (address>=self.Min) and (address<=self.Max):
            return True
        else:
            return False
        
    def correct_overflow(self, value: int):
        ## capping values, such they do not exceed value bounds ##
        if value < -self.maxint:
            value = -self.maxint
        elif value > self.maxint:
            value = self.maxint
        else:
            value = value

        return value

if __name__ == "__main__":
    sp = 100                # must be positive integer
    sw = 100                # must be positive integer
    maxint = 10000          # according to paper

    um = UniversalMachine(
        sp=sp,
        sw=sw,
        maxint=maxint,
        max_memory_alloc=5
    )

    program_tape = [
        7,2,
        4,0,-1,-1,
        10,1,-1,-1,
        0,-2,-1,6,
        12,1,
        6,-1,-2,
        8,-1,
        9,-2,
        5,3,-1,
        3
    ]
    
    um.init_program_tape(program_tape)
    um.init_work_tape([])
    um.init_input_tape([maxint+1])
    um.run(max_steps=100)
    print(um.output_tape)
    print(um.work_tape)

# TODO:
# Handle overflow of cells for program tape and work tape [DONE]
# Check that instructions can only write to addresses on work tape [DONE]
# Check that based on the address the machine either manipulates the work tape or the program tape [DONE]
# Print why the machine has halted []

# Test instruction: [DONE]
# -----------------
## JUMPLEQ   [DONE]
## OUTPUT    [DONE]
## JUMP      [DONE]
## STOP      [DONE]
## ADD       [DONE]
## GET_INPUT [DONE]
## MOVE      [DONE]
## ALLOCATE  [DONE]
## INCREMENT [DONE]
## DECREMENT [DONE]
## SUBTRACT  [DONE]
## MULTIPLY  [DONE]
## FREE      [DONE]
