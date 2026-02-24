
import os

words = set()
DEFAULT_MAX_LADDER_LENGTH = 8

def main():
    help()
    while True:
        print("\n> ",end="")
        tokens = input().split()
        if len(tokens) == 0 or tokens[0].upper() == "HELP":
            help()
        elif tokens[0].upper() in ["QUIT","Q"]:
            break
        elif tokens[0].upper() in ["LOAD","L"]:
            if len(tokens) != 2:
                print("Usage: LOAD <filepath>")
            else:
                load_words(tokens[1])
        elif tokens[0].upper() in ["SAVE","S"]:
            if len(tokens) != 2:
                print("Usage: SAVE <filepath>")
            else:
                save_words(tokens[1])
        elif tokens[0].upper() in ["ADD","A","+"]:
            for new_word in tokens[1:]:
                new_word = new_word.upper()
                if not new_word.isalpha():
                    print(f"{new_word} ignored, contains non-alpha characters")
                elif new_word in words:
                    print(f"{new_word} ignored, already in known words")
                else:
                    words.add(new_word)
                    print(f"{new_word} learned")
        elif tokens[0].upper() in ["REMOVE","R","-"]:
            for word_to_remove in tokens[1:]:
                word_to_remove = word_to_remove.upper()
                if word_to_remove not in words:
                    print(f"{word_to_remove} ignored, not in known words")
                else:
                    words.remove(word_to_remove)
                    print(f"{word_to_remove} unlearned")
        elif tokens[0].upper() in ["EXPLORE","X"]:
            if len(tokens) != 2:
                help()
            else:
                query_word = tokens[1].upper()
                print("Insertions:")
                for w in sorted(insertion_words(query_word)):
                    print(f"\t{w}")
                print("Deletions:")
                for w in sorted(deletion_words(query_word)):
                    print(f"\t{w}")
                print("Replacements:")
                for w in sorted(replacement_words(query_word)):
                    print(f"\t{w}")
                print("Rearrangements:")
                for w in sorted(anagrams(query_word)):
                    print(f"\t{w}")
        elif tokens[0].upper() in ["LADDER","D"]:
            if not 3 <= len(tokens) <= 4:
                help()
                continue
            
            if len(tokens) == 3:
                max_ladder_length = DEFAULT_MAX_LADDER_LENGTH
            elif len(tokens) == 4:
                if not tokens[3].isdigit():
                    help()
                    continue
                max_ladder_length = int(tokens[3])
            
            word1 = tokens[1].upper()
            word2 = tokens[2].upper()
            paths = find_paths(word1,word2,max_ladder_length)
            if len(paths) > 0:
                print(f"Word ladders from {word1} to {word2}")
                for path in sorted(paths):
                    print("\t" + ">".join(path))
            else:
                print("No ladders found up to max ladder_length.")
            
                
        else:
            print(f"Command \"{tokens[0]}\" not recognized.")

def help():
    print(f"{len(words)} words currently known")
    print("Options:")
    print("HELP")
    print("QUIT/Q")
    print("LOAD/L <filepath> - load alpha-only words from a \\n-separated file")
    print("SAVE/S <filepath> - write current list of words to an \\n-separated file")
    print("ADD/A/+ <words...> - add individual words to the dictionary")
    print("REMOVE/R/- <words...> - remove individual words from the dictionary")
    print("EXPLORE/X <word> - print all known words that can be formed by inserting, deleting, or replacing one letter; or rearranging all letters")
    print(f"LADDER/D <word1> <word2> - search for word ladders connecting word1 to word2 to a preset depth of {DEFAULT_MAX_LADDER_LENGTH}")
    

def load_words(filepath):
    new_words = set()
    non_alpha_count = 0
    try:
        with open(filepath) as fin:
            for line in fin:
                new_word = line.rstrip().upper()
                if new_word.isalpha():
                    new_words.add(new_word)
                else:
                    non_alpha_count += 1
        already_known_count = len(new_words & words)
        words.update(new_words)
        print(f"Read {len(new_words)} words from {filepath}")
        print(f"{non_alpha_count} rejected, non-alpha")
        print(f"{already_known_count} already known")
        print(f"{len(new_words) - already_known_count} new words learned")
    except:
        print(f"Error with filepath \"{filepath}\"")

def save_words(filepath):
    if os.path.isfile(filepath):
        print(f"File \"{filepath}\" already exists. Type \"yes\" to confirm.")
        if input().lower() != "yes":
            print("Saving aborted")
            return
    
    try:
        with open(filepath,"w") as fout:
            for word in sorted(words):
                fout.write(f"{word}\n")
    except:
        print("Error writing to \"{filepath}\"")

def check_indel(short_word,long_word):
    for i in range(len(long_word)):
        if long_word[:i] + long_word[i+1:] == short_word:
            return True
    return False
    
def hamming_distance(word1,word2):
    distance = 0
    for i in range(len(word1)):
        if word1[i] != word2[i]:
            distance += 1
    return distance

def insertion_words(query_word):
    return {w for w in words if len(w) - 1 == len(query_word) and check_indel(query_word,w)}

def deletion_words(query_word):
    return {w for w in words if len(w) + 1 == len(query_word) and check_indel(w,query_word)}

def replacement_words(query_word):
    return {w for w in words if len(w) == len(query_word) and hamming_distance(query_word,w) == 1}

def anagrams(query_word):
    return {w for w in words if sorted(query_word) == sorted(w) and query_word != w}

def find_paths(word1,word2,max_ladder_length):
    
    paths1 = [[word1]]
    paths2 = [[word2]]
    
    return find_paths2(paths1,paths2,max_ladder_length,2,set(),set())

def find_paths2(paths1,paths2,max_ladder_length,ladder_length,words_traversed1,words_traversed2):
    
    # check if we've connected paths1 to paths2 anywhere
    full_paths = []
    for path1 in paths1:
        for path2 in paths2:
            # if the last word reached in both paths is the same, we've linked up
            if path1[-1] == path2[-1]:
                full_paths.append(path1 + path2[::-1][1:])
    if len(full_paths) > 0:
        return full_paths
    
    # have we searched as far as we're willing?
    if ladder_length > max_ladder_length:
        return []
    
    print(f"Searching for ladders of length {ladder_length}...")
    
    if ladder_length % 2 == 0:
        selected_paths = paths1
        selected_words_traversed = words_traversed1
    else:
        selected_paths = paths2
        selected_words_traversed = words_traversed2
    
    new_paths = []
    new_words_traversed = set()
    for path in selected_paths:
        last_word = path[-1]
        for connected_word in replacement_words(last_word) - selected_words_traversed:
            new_paths.append(path + [connected_word])
            new_words_traversed.add(connected_word)
    
    if ladder_length % 2 == 0:
        paths1 = new_paths
        words_traversed1 |= new_words_traversed
    else :
        paths2 = new_paths
        words_traversed2 |= new_words_traversed
    
    return find_paths2(paths1,paths2,max_ladder_length,ladder_length+1,words_traversed1,words_traversed2)
    
    

if __name__ == "__main__":
    main()