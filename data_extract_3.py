'''
Written by Joseph Ma
7/16/22
'''
import pandas as pd
import random as r
import math as m

GRAY = "\033[2;48;5;243m\033[38;5;255m"
YELLOW = "\033[2;48;5;3m\033[38;5;248m"
GREEN = "\033[2;48;5;10m\033[38;5;248m"
RESET = "\033[2;48;5;10m\033[0m"

#game host function takes in an answer and guess, returns 
#output as feedback 
def game_host(answer, guess):
  hints = ""
  letters = list(guess) 

  #create a dictionary to keep track of how many times a letter has been marked green/yellow
  count_green = dict.fromkeys(letters, 0)
  count_yellow = dict.fromkeys(letters, 0)

  #first determine how many greens are there 
  #because number of greens determine number of yellows allowed
  for i in range(len(guess)):
    if(guess[i] == answer[i]):
      count_green[guess[i]] += 1
  
  for i in range(len(guess)):
    if((guess[i] != answer[i]) and (guess[i] in answer) and (answer.count(guess[i]) > (count_green[guess[i]] + count_yellow[guess[i]]))):
      #the letter is not in that spot
      #the letter is elsewher in the word
      #the number of occurences of that letter in the word is more than that of the currently recorded green + yellow
      count_yellow[guess[i]] += 1

  for i in range(len(guess)):
    if(guess[i] not in answer):
      hints += "W"      #GRAY
    elif(guess[i] == answer[i]):
      hints += "G"      #GREEN
    elif((guess[i] != answer[i]) and (guess[i] in answer) and (count_yellow[guess[i]] != 0)):
      #last condition is to ensure we don't overmark yellow letters
      hints += "Y"      #YELLOW
      count_yellow[guess[i]] -= 1
    else:
      hints += "W"
    
  return hints

def show_feedback(hints, guess):
  colored_string = ""
  for i in range(len(guess)):
    if(hints[i] == "G"):
      colored_string += GREEN + guess[i]
    elif(hints[i] == "Y"):
      colored_string += YELLOW + guess[i]
    else:
      colored_string += GRAY + guess[i]
  return colored_string

def all_words(i):
  df = pd.read_csv("allowed_words.txt")
  #extract the words of the desired length
  df_filtered = df[df["Word"].str.len() == i]

  #create a list of list of seperated letters
  data = []
  for x in range(len(df_filtered)):
    word = df_filtered.values[x][0]
    word_list = list(word)
    word_list.insert(0, word)
    
    data.append(word_list)

  #create a data frame with column consisting of letters in each word
  len_word = i   #number of letters
  column_vals = ["Word"]
  for x in range(len_word):
    column_vals.append("letter_" + str(x + 1))

  letters = pd.DataFrame(data, columns=column_vals)
  return letters

def all_words_2(i):
  df = pd.read_csv("answers.txt")
  #extract the words of the desired length
  df_filtered = df[df["Word"].str.len() == i]

  #create a list of list of seperated letters
  data = []
  for x in range(len(df_filtered)):
    word = df_filtered.values[x][0]
    word_list = list(word)
    word_list.insert(0, word)
    
    data.append(word_list)

  #create a data frame with column consisting of letters in each word
  len_word = i   #number of letters
  column_vals = ["Word"]
  for x in range(len_word):
    column_vals.append("letter_" + str(x + 1))

  letters = pd.DataFrame(data, columns=column_vals)
  return letters

#get list takes in the feedback colors, the guess, df of words and returns the conditionals
def get_conditions(feedback, guess, df):
  #CONDITION EVALUATION
  yellow_letter = []
  green_letter = []
  grey_letter = []

  #Green CONDITIONS
  condition_created = False
  for i in range(len(feedback)):
    if(feedback[i] == "G"):
      green_letter.append(guess[i])
      if(condition_created == False):
        conditions_green = df["letter_" + str(i + 1)] == guess[i]             #checks if that letter is in that spot
        condition_created = True
      else:
        conditions_green = conditions_green & (df["letter_" + str(i + 1)] == guess[i])    #IMPORTANT: need brackets because & takes precdence
  if(condition_created == False):
    conditions_green = df["letter_1"] == df["letter_1"]     #create arbritrary True statements since we are ANDing them at the end anyways

  #Yellow CONDITIONS
  condition_created = False
  for i in range(len(feedback)):
    if(feedback[i] == "Y"):
      yellow_letter.append(guess[i])    

      if(condition_created == False):
        conditions_yellow = df["Word"].str.contains(guess[i]) & (df["letter_" + str(i + 1)] != guess[i])      #checks if that letter is included in the word AND is not in that position
        condition_created = True
      else:
        conditions_yellow = conditions_yellow & (df["Word"].str.contains(guess[i]) & (df["letter_" + str(i + 1)] != guess[i]))
  if(condition_created == False):
    conditions_yellow = df["letter_1"] == df["letter_1"]     #create arbritray True statements since we are ANDing them at the end anyways

  #Grey CONDITIONS
  condition_created = False
  for i in range(len(feedback)):
    if(feedback[i] == "W"):
      grey_letter.append(guess[i])
      if(guess[i] not in yellow_letter and guess[i] not in green_letter):
        #ONLY apply the grey condition-(letter does not appear in the word) if that letter has not been marked yellow or green
        if(condition_created == False):
          conditions_grey = ~df["Word"].str.contains(guess[i])
          condition_created = True
        else:
          conditions_grey = conditions_grey & (~df["Word"].str.contains(guess[i]))      #checks if that letter is not included in the word
      else:
        #IF that letter has been marked yellow or green somewhere- we can only deduce that letter is NOT in that spot
        #example: PILLS- if first L is yellow and second L is grey, we can only deduce second L is not in the spot of the fourth letter
        if(condition_created == False):
          conditions_grey = df["letter_" + str(i + 1)] != guess[i]
          condition_created = True
        else:
          conditions_grey = conditions_grey & (df["letter_" + str(i + 1)] != guess[i])

  if(condition_created == False):
    conditions_grey = df["letter_1"] == df["letter_1"]     #create arbritray True statements since we are ANDing them at the end anyways
        
  #CONDITION COUNT GREEN + YELLOW
  condition_created = False
  #check word count according to yellow letter list- for example in PILLS- if the first L is yellow and second is not, we know there must be at least 1 L in the word + number of green L's
  green_yellow_letters = green_letter + yellow_letter

  unique_gy_letters = list(set(green_yellow_letters))
  for letter in unique_gy_letters:
    count = yellow_letter.count(letter) + green_letter.count(letter)    #see how many times that letter was colored yellow and green
    if(letter not in grey_letter):
      #the letter has to appear AT LEAST the number of times it has been green + yellow
      if(condition_created == False):
        conditions_repeat = df["Word"].str.count(letter) >= count
        condition_created = True
      else:
        conditions_repeat = conditions_repeat & (df["Word"].str.count(letter) >= count)
    else:
      #the letter has to appear EXACTLY the number of times it has been green + yellow
      if(condition_created == False):
        conditions_repeat = df["Word"].str.count(letter) == count
        condition_created = True
      else:
        conditions_repeat = conditions_repeat & (df["Word"].str.count(letter) == count)

  if(condition_created == False):
    conditions_repeat = df["letter_1"] == df["letter_1"]     #create arbritray True statements since we are ANDing them at the end anyways

  return (conditions_green & conditions_grey & conditions_yellow & conditions_repeat)

df = all_words(5)
#answers = pd.read_csv("answers.txt")
answers = all_words_2(5)
data_vals = pd.read_csv("answers.txt")
data = [0] * len(data_vals)
column_vals = ["Num Guesses"]
vals = pd.DataFrame(data, columns = column_vals)
data_vals = pd.concat([data_vals, vals], axis = 1)

for i in range(14):
  data = [0] * len(data_vals)
  column_vals = ["Attempt " + str(i + 1)]
  vals = pd.DataFrame(data, columns = column_vals)
  data_vals = pd.concat([data_vals, vals], axis = 1)

bit_vals = pd.read_csv("answers.txt")
data = [0] * len(data_vals)
column_vals = ["Num Guesses"]
vals = pd.DataFrame(data, columns = column_vals)
bit_vals = pd.concat([bit_vals, vals], axis = 1)

for i in range(14):
  data = [0.0] * len(bit_vals)
  column_vals = ["Attempt " + str(i + 1)]
  vals = pd.DataFrame(data, columns = column_vals)
  bit_vals = pd.concat([bit_vals, vals], axis = 1)

guess_history = pd.read_csv("answers.txt")
data = [0] * len(data_vals)
column_vals = ["Num Guesses"]
vals = pd.DataFrame(data, columns = column_vals)
guess_history = pd.concat([guess_history, vals], axis = 1)
for i in range(14):
  data = [""] * len(data_vals)
  column_vals = ["Attempt " + str(i + 1)]
  vals = pd.DataFrame(data, columns = column_vals)
  guess_history = pd.concat([guess_history, vals], axis = 1)

win_chance = pd.read_csv("answers.txt")
data = [0] * len(win_chance)
column_vals = ["Num Guesses"]
vals = pd.DataFrame(data, columns = column_vals)
win_chance = pd.concat([win_chance, vals], axis = 1)
for i in range(14):
  data = [0.0] * len(win_chance)
  column_vals = ["Attempt " + str(i + 1)]
  vals = pd.DataFrame(data, columns = column_vals)
  win_chance = pd.concat([win_chance, vals], axis = 1)


#see how well it does with random selection from list of possible words
for i in range(len(answers)):
  #i = r.randint(0, len(answers))

  #iterate through the answers
  filtered = df
  green_index = [0] * 5
  conditions = df["letter_1"] == df["letter_1"]     #a list of true conditions

  #data conditions prevent us from guessing the same letter in the same spot again
  data_conditions = [df["letter_1"] == df["letter_1"]] * len(green_index)  

  guess_count = 0
  prev_filtered = 0
  found_green = False
  
  guessed = False
  while(not guessed):
    if guess_count == 0:
      word_guess = "tares"    #best starter word
    else:
      if len(filtered) == 1:    
        #we only have one more choice
        word_guess = filtered.values[0][0]
      else:
        letters_of_interest = []
        check_letters = []
        for j in range(len(green_index)):
          if green_index[j] == 0:
          #this position in the word is currently uncertain and not green
          #find the most freuently appearing uncertain letters in each position
            letters_of_interest.append(filtered["letter_" + str(j + 1)].value_counts().index.tolist()[:26])#len(green_index)
            #print(filtered["letter_" + str(j + 1)].value_counts())
          else:
            letters_of_interest.append([])  #otherwise append an empty list to that position


        #prioritize the letters based on the most frequently appearing in each index
        for j in range(len(green_index)):
          for k in range(len(green_index)):
            if(len(letters_of_interest[k]) >= j + 1):
              check_letters.append(letters_of_interest[k][j])

        #eliminate duplicates but keep the order
        priority_letters = []
        for j in range(len(check_letters)):
          if(check_letters[j] not in priority_letters):
            priority_letters.append(check_letters[j])
        index_ctr = 0
        optimized = False
        check_conditions = df["letter_1"] == df["letter_1"]
        for j in range(len(data_conditions)):
          check_conditions = check_conditions & data_conditions[j]
        filtered_df = df[check_conditions]

        num_priority = len(green_index) - sum(green_index)    #this tells us how many uncertain columns we have
        
        priority_letters = check_letters    #testing
        while(len(filtered_df) > 1 and optimized == False and len(priority_letters[index_ctr: index_ctr + num_priority]) > 0):
          letters_set = set(priority_letters[index_ctr: index_ctr + num_priority])

          df_set = filtered_df["Word"].apply(set)
          #print(df_set)
          for j in range(len(df_set)):
            df_set[df_set.index[j]] = len(df_set[df_set.index[j]].intersection(letters_set))
          if df_set.max() == len(green_index):
            optimized = True   #we have words that match the first 5 letters

          filtered_df = filtered_df[df_set == df_set.max()]
          '''
          print("update")
          print(filtered_df)
          '''
          if(len(filtered_df) != 1):
            word_guess = filtered_df.values[r.randint(0, len(filtered_df) - 1)][0]
          elif(len(filtered_df) != 0):
            word_guess = filtered_df.values[0][0]
          index_ctr += num_priority

    
    for j in range(len(word_guess)):
        #add the conditions such that we will not repeatedly guess the same letter in the same position
        data_conditions[j] = data_conditions[j] & (df["letter_" + str(j + 1)] != word_guess[j])

    guess_history.at[i, "Attempt " + str(guess_count + 1)] = word_guess

    hints = game_host(answers.values[i][0], word_guess)              #feedback "GGYWW"
    #hints = game_host("fleet", word_guess)              #feedback "GGYWW"

    if "G" in hints:
      found_green = True
    
    conditions = conditions & get_conditions(hints, word_guess, answers)    #AND all previous conditions (LAST ARGUMENT DF CHANGED TO FILTERD)
    
    filtered = answers[conditions]
    
    #filtered = df[conditions]
    for j in range(len(hints)):
      if green_index[j] == 0:
        #we should check if that column has uncertainty
        if (filtered['letter_' + str(j + 1)].values == filtered['letter_' + str(j + 1)].values[0]).all():
          green_index[j] = 1

          #data_conditions[j] = data_conditions[j] & (df["letter_" + str(j + 1)] != filtered["letter_" + str(j+1)].values[0])

    if(word_guess == answers.values[i][0]):
      #if(word_guess == "fleet"):
      #the answer was guessed
      data_vals.at[i, "Num Guesses"] = guess_count + 1
      guess_history.at[i, "Num Guesses"] = guess_count + 1
      bit_vals.at[i, "Num Guesses"] = guess_count + 1
      win_chance.at[i, "Num Guesses"] = guess_count + 1
      guessed = True
    else:
      data_vals.at[i, "Attempt " + str(guess_count + 1)] = len(filtered)
      win_chance.at[i, "Attempt " + str(guess_count + 1)] = 100 / len(filtered)
      if(guess_count == 0):
        #we are on our first iteration
        bit_vals.at[i, "Attempt " + str(guess_count + 1)] = m.log(len(filtered) / len(df)) / m.log(0.5)
      else:
        bit_vals.at[i, "Attempt " + str(guess_count + 1)] = m.log(len(filtered) / prev_filtered) / m.log(0.5)
    guess_count += 1
    prev_filtered = len(filtered)
