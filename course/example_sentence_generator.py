def example_generator(input_word):
    from googletrans import Translator
    translator = Translator()
    translations = translator.translate(input_word,src='en' ,dest='zh-tw')
    translations_dict = translations.extra_data
    examples_len = len(translations_dict['examples'])

    if examples_len > 0:
        examples_len = len(translations_dict['examples'][0])
    else:
        print('沒有例句')
    # 還原詞性

    from nltk.corpus import wordnet
    from nltk import word_tokenize, pos_tag
    from nltk.stem import WordNetLemmatizer


    def get_wordnet_pos(treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return None


    def lemmatize_sentence(sentence):
        # res = []
        res = {}
        
        lemmatizer = WordNetLemmatizer()
        for word, pos in pos_tag(word_tokenize(sentence)):
            wordnet_pos = get_wordnet_pos(pos) or wordnet.NOUN
            # res.append(lemmatizer.lemmatize(word, pos=wordnet_pos))
            res.update({lemmatizer.lemmatize(word, pos=wordnet_pos):wordnet_pos})
        return res

    import codecs
    word_dict={}
    cont=''
    with codecs.open('7000單字.txt', 'r', encoding='utf8') as f:
        for line in f:
            tmp = line.split('\t')
            word_dict.update({tmp[0]:tmp[1]})

    tag_2google = {'a':'adjective',
                'n':'noun',
                'v':'verb'
            }
    def hava_difficult_words(row_words): #檢查句子 有無沒有在7000單字裡的難字 並回傳json
        output_json={}
        difficult=0
        ez=0
        for i in range(len(row_words)):
            # row_word = list(res.keys())[i] #為啥要這樣寫?
            row_word = list(row_words.keys())[i]
            if row_word.isalpha(): #判斷是否是英文
                if row_word.lower() in word_dict: #判斷是否有在7000單字內
                    ez += 1
                elif row_word.istitle(): #判斷是否首字大寫，大寫的話代表專有名詞
                    if i==1: #句子開頭
                        # print("difficult:",row_word)
                        # print(list(res.values())[i])
                        output_json.update({difficult:{'difficult:':row_word,'tag':tag_2google[list(row_words.values())[i]]}})
                        difficult+=1
                    else:
                        ez += 1
                        #因為既然不在7000單字內，而且又不是句子開頭那就代表是專有名詞，不須替換
                else:
                    # print("difficult:",row_word)
                    # print(list(res.values())[i])
                    output_json.update({difficult:{'difficult':row_word,'tag':tag_2google[list(row_words.values())[i]]}})
                    difficult+=1
        return output_json

    def nltk_synonyms(difficult_words_json):
        # 如果有非7000單字 就去搜尋同意字替換
        # nltk方法
        
        import nltk 
        from nltk.corpus import wordnet 

        output_json={}

        for i in difficult_words_json:
            word_synonyms = []
            for syn in wordnet.synsets(difficult_words_json[i]['difficult']): 
                for l in syn.lemmas():
                    if (l.name().lower() in word_dict) and (l.name().lower() != difficult_words_json[i]['difficult']) and not (l.name().lower() in word_synonyms):
                        # 如果有在7000單字內 且 不重複
                        word_synonyms.append(l.name().lower())
            output_json.update({i:word_synonyms})

        return output_json

    def google_synonyms(difficult_words_json):
        output_json={}
        for i in difficult_words_json:
            synonyms_translations = translator.translate(difficult_words_json[i]['difficult'],src='en')
            synonyms_translations_dict = synonyms_translations.extra_data
            word_synonyms = []
            tag_flag = ''
            for j in difficult_words_json: #因為不是len判斷，所以可能會有非數字的情形這樣的話程式就會出錯
                if synonyms_translations_dict['synonyms'] != None:
                    for tags in synonyms_translations_dict['synonyms']:
                        for tag in tags:
                            if isinstance(tag,str):
                                #print('tag',tag)
                                tag_flag = tag   
                            elif isinstance(tag,list):
                                for synonyms in tag:
                                    for words in synonyms:
                                        if isinstance(words,list):
                                            for word in words:
                                                #print('word',word)
                                                if (tag_flag == difficult_words_json[j]['tag']) and (word in word_dict) and not (word in word_synonyms): #如果是相同詞性而且是在7000單字裡
                                                    word_synonyms.append(word)
            output_json.update({i:word_synonyms})  
        return output_json


    # for examples_len in range(len(translations_dict['examples'][0]) if len(translations_dict['examples'][0])<30 else 30):
    output_examples=[]
    output_json={}
    i = 0
    for examples_len in range(len(translations_dict['examples'][0])):
        
        example = translations_dict['examples'][0][examples_len][0]
        example = (example[:example.find('<b>')]+ input_word +example[example.find('</b>')+4:])
        row_words = lemmatize_sentence(example)
        
        difficult_words_json = hava_difficult_words(row_words)
        if difficult_words_json == {}:
            # print("全句都符合7000單字難度",example)
            output_examples.append(example)
            output_json.update(
                {
                    i:{
                        'example':example,
                        'difficults':None,
                        'nltk':None,
                        'google':None
                    }
                }
            )
            i+=1
        else:   
            # print(difficult_words_json,example)
            from_nltk_synonyms = nltk_synonyms(difficult_words_json)
            from_google_synonyms = google_synonyms(difficult_words_json)
            if (from_nltk_synonyms != {0: []}) or (from_google_synonyms != {0: []}):
                # print(from_nltk_synonyms) 
                # print(from_google_synonyms)
                output_json.update(
                    {
                        i:{
                            'example':example,
                            'difficults':difficult_words_json,
                            'nltk':from_nltk_synonyms,
                            'google':from_google_synonyms
                        }
                    }
                )
                i+=1
    return output_json

if __name__ == '__main__':
    print(example_generator('program'))  # 或是任何你想執行的函式
