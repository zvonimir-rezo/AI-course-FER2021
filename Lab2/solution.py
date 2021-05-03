import sys
import re

counter = 1


def main():
    cook = False
    for i in range(len(sys.argv)):
        if sys.argv[i] == "resolution":
            resolution = True
            resolution_examples_path = sys.argv[i + 1]
        elif sys.argv[i] == "cooking":
            cook = True
            cooking_examples_path = sys.argv[i + 1]
            user_commands_path = sys.argv[i + 2]

    clauses = []
    commands = []
    if cook:
        with open(f"{cooking_examples_path}", "r", encoding="utf8") as file:
            lines = file.read().strip().lower().split("\n")
            for i in range(len(lines)):
                if lines[i].startswith("#"):
                    continue
                clauses.append(lines[i].split(" v "))

        with open(f"{user_commands_path}", "r", encoding="utf8") as file:
            lines = file.read().strip().lower().split("\n")
            for i in range(len(lines)):
                if lines[i].startswith("#"):
                    continue
                res = re.search(r'[+-\\?]', lines[i])
                index = res.start()
                clause = lines[i][:index-1]
                command = lines[i][index]
                commands.append([clause, command])
        for command in commands:
            if command[1] == "-":
                dels = []
                for i in range(len(clauses)):
                    if clauses[i] == command[0].split(" v "):
                        dels.append(i)
                for i in sorted(dels, reverse=True):
                    del clauses[i]
            elif command[1] == "+":
                clauses.append(command[0].split(" v "))
            elif command[1] == "?":
                clauses_copy = clauses[:]
                pl_resolution(clauses_copy, [command[0]])
    elif resolution:
        with open(f"{resolution_examples_path}", "r", encoding="utf8") as file:
            lines = file.read().strip().lower().split("\n")
            end_clause = lines[len(lines)-1]
            for i in range(len(lines)-1):
                if lines[i].startswith("#"):
                    continue
                clauses.append(lines[i].split(" v "))
        # clauses je lista listi
        pl_resolution(clauses, end_clause.split(" v "))


def pl_resolution(clauses, end_clause):
    global counter
    end_clause_negated = negate_clause(end_clause)
    all_clauses = clauses
    all_clauses.extend(end_clause_negated)
    result_string = ""
    counter = 1
    for i in all_clauses:
        result_string += (f"{counter}. " + " v ".join(i) + "\n")
        counter += 1
    sos = end_clause_negated
    while True:
        all_clauses = deletion_strategy(all_clauses)
        for cl in sos:
            if list(cl) not in all_clauses:
                sos.remove(cl)
        sos_new, found_nil, result_string = pl_resolve(all_clauses, sos, result_string)
        if found_nil:
            print_relevant(result_string)
            print(f"[CONCLUSION]: {' v '.join(end_clause)} is true")
            break
        sos = list(sos_new)
        contains_all = True
        for clause in sos:
            list_clause = list(clause)
            if list_clause not in all_clauses:
                contains_all = False
                break
        if contains_all:
            print(f"[CONCLUSION]: {' v '.join(end_clause)} is unknown")
            break
        for cl in sos:
            list_cl = list(cl)
            all_clauses.extend([list_cl])


def pl_resolve(all_clauses, sos, result_string):
    global counter
    sos_list = []
    for sos_tuple in sos:
        sos_list.append(list(sos_tuple))
    sos_set = set()
    for i in range(len(sos_list)):
        for j in range(len(all_clauses)):
            negated_clause = negate_literals(all_clauses[j])
            for k in range(len(all_clauses[j])):
                if negated_clause[k] in sos_list[i]:
                    if len(all_clauses[j]) == 1 and len(sos_list[i]) == 1:
                        sos_set.update(["NIL"])
                        result_string += f"{counter+1}. " + "NIL" + f" ({all_clauses[j]}, {sos_list[i]})" + "\n"
                        return sos_set, True, result_string
                    clause_copy = all_clauses[j][:]
                    sos_clause_copy = sos_list[i][:]
                    atom = clause_copy.pop(k)
                    sos_clause_copy.pop(sos_list[i].index(negate_literal(atom)))
                    final_clause_set = set(clause_copy)
                    final_clause_set.update(sos_clause_copy)
                    final_clause_tuple = tuple(final_clause_set)
                    result_string += f"{counter}. " + " v ".join(final_clause_tuple) + f" ({all_clauses[j]}, {sos_list[i]})" + "\n"
                    counter += 1
                    sos_set.update([final_clause_tuple])

    return sos_set, False, result_string


def deletion_strategy(clauses):
    indexes = set()
    for i in range(len(clauses)):
        if is_tautology(clauses[i]):
            indexes.add(i)
            continue
        for j in range(len(clauses)):
            if i != j and all(literal in clauses[i] for literal in clauses[j]):
                indexes.add(i)
    for i in sorted(list(indexes), reverse=True):
        clauses.pop(i)
    return clauses


def is_tautology(clause):
    for literal in clause:
        if negate_literal(literal) in clause:
            return True
    return False


def negate_literals(clause):
    negated_literals = []
    for lit in clause:
        if lit.startswith("~"):
            negated_literals.append(lit[1:])
        else:
            negated_literals.append("~" + lit)
    return negated_literals


def negate_clause(clause):
    negated_literals = []
    for lit in clause:
        if lit.startswith("~"):
            negated_literals.append(lit[1:])
        else:
            negated_literals.append("~" + lit)
    clauses = []
    for lit in negated_literals:
        clauses.append([lit])
    return clauses


def negate_literal(literal):
    if literal.startswith("~"):
        return literal[1:]
    else:
        return "~" + literal


def print_relevant(result_string):
    splitted_string = result_string.rstrip("\n").split("\n")
    only_clauses = []
    for i in splitted_string:
        start = i.index(' ')
        try:
            end = i.index('(')-1
        except ValueError:
            end = len(i)
        only_clauses.append(i[start:end].strip(" "))
    for i in range(len(splitted_string)):
        if '[' not in splitted_string[i]:
            continue
        matches = re.findall(r'\[.*?\]', splitted_string[i])
        first_clause = matches[0][1:-1]
        second_clause = matches[1][1:-1]
        quotes_removed_first = first_clause.replace("'", "")
        quotes_removed_second = second_clause.replace("'", "")
        clause_final_first = " v".join(quotes_removed_first.split(','))
        clause_final_second = " v".join(quotes_removed_second.split(','))

        splitted_string[i] = splitted_string[i].replace("[" + first_clause + "]",
                                                        str(only_clauses.index(clause_final_first)+1))
        splitted_string[i] = splitted_string[i].replace("[" + second_clause + "]",
                                                        str(only_clauses.index(clause_final_second)+1))
    clauses_to_work = []
    current_clause = splitted_string[-1]
    end_list = [current_clause]
    while "(" in current_clause or clauses_to_work:
        if "(" not in current_clause:
            current_clause = splitted_string[clauses_to_work.pop(0)]
            continue
        first_index = int(current_clause[current_clause.index('(')+1:current_clause.index(',')])-1
        second_index = int(current_clause[current_clause.index(',')+1:current_clause.index(')')])-1
        clauses_to_work.append(first_index)
        clauses_to_work.append(second_index)
        end_list.insert(0, splitted_string[first_index])
        end_list.insert(0, splitted_string[second_index])
        current_clause = splitted_string[clauses_to_work.pop(0)]

    end_list = sorted(end_list, key=lambda x: int(x[:x.index('.')]))
    end_str = "\n".join(end_list)
    replacements = {}
    for i in range(len(end_list)):
        replacements[end_list[i][:end_list[i].index('.')]] = i+1

    for old, repl in replacements.items():
        end_str = end_str.replace(old + ".", str(repl) + ".")
        end_str = end_str.replace("(" + old, "(" + str(repl))
        end_str = end_str.replace(old + ")", str(repl) + ")")

    print(end_str)


if __name__ == "__main__":
    main()