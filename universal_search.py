from universal_machine import UniversalMachine

class UniversalSearch():
    def __init__(self, instructions: list):
        self.candidate_list = []
        self.index_to_instruction_map = {i:instr for i, instr in enumerate(instructions)}
        self.instructions_to_index_map = {instr:i for i, instr in enumerate(instructions)}
        self.solution = None

    def get_next_prgram(self, current_program):
        new_program = current_program.copy()
        for i,instr in enumerate(reversed(current_program)):
            if self.instructions_to_index_map[instr]+1 in self.index_to_instruction_map.keys():
                new_program[-(i+1)] = self.index_to_instruction_map[self.instructions_to_index_map[instr]+1]
                return new_program
            else:
                new_program[-(i+1)] = self.index_to_instruction_map[0]
        new_program.append(self.index_to_instruction_map[0])
        return new_program
    
    def search(self):
        current_program = []
        solution_found = False
        while solution_found == False:
            next_program = self.get_next_prgram(current_program)
            current_program = next_program.copy()
            um = UniversalMachine(
                sp=100,
                sw=100,
                maxint=10000,
                max_memory_alloc=5
            )
            um.init_program_tape(current_program)
            um.init_work_tape([])
            um.init_input_tape([])
            active = True
            self.candidate_list.append([um, active])

            solution_found = self.run_candidate_programs()
        
        print("Solution found!")
        return self.solution

    def run_candidate_programs(self):
        solution_found = False
        for i in range(len(self.candidate_list)):
            um, active = self.candidate_list[i]
            if active == True:
                #print(f"program tape: {um.program_tape}, active: {active}")
                if um.instruction_pointer < len(um.program_tape):
                    instruction = um.program_tape[um.instruction_pointer]
                    HALT = um.execute_instruction(instruction)
                else:
                    HALT = True
                if HALT == True:
                    solution_found = self.evaluate_program_output(um)
                    if solution_found == None:
                        raise Exception("Must be implemented by user, depending on use case!")
                    elif solution_found == True:
                        return solution_found
                    else:
                        self.candidate_list[i][1] = False
        
        return solution_found

    def evaluate_program_output(self, um):
        """
        Needs to implemented for specific use case.
        Solution needs to be stored in 'self.solution'.
        """
        return None
        
class UniversalFactor(UniversalSearch):
    def __init__(self, number: int):
        self.number = number
        super().__init__([0,1,2,3,4,5,6,7,8,9,10,11,12])

    def evaluate_program_output(self, um):
        solution_found = False
        if len(um.output_tape) > 0:
            candidate_factor = um.output_tape[0]
            if candidate_factor > 1:
                if (self.number%candidate_factor == 0):
                    self.solution = candidate_factor
                    self.solution_program_tape = um.program_tape
                    self.solution_output_tape = um.output_tape
                    solution_found = True
        
        return solution_found
            
            
        
if __name__ == "__main__":
    uf = UniversalFactor(13)
    uf.search()
    print("Solution: ", uf.solution)
    print("Program tape: ", uf.solution_program_tape)
    print("Output tape", uf.solution_output_tape)

# ToDo
# comment code []
# modularize better, don't want to provide instruction set when defining specific problem class []
# probably make interface for universal search base class and universal machine? []
# add exponential search time to shorter programs (add resource scheduler) []
# improve program generation, check if already halted program (halted because finished->halt command/invalid command, or end of Tape?) is prefix of currently generated program []
# make search usable from command line, specifying problem specific parameters, evaluation function, and resource scheduling []
