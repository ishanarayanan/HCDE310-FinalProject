
# Value: add a max food cost to user input, if it is above the price limit dont include it 


import urllib.parse, urllib.request, urllib.error, json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import urllib.parse, urllib.request, urllib.error, json

from flask import Flask, render_template, request
import logging

app = Flask(__name__)

@app.route("/")
def main_handler():
    app.logger.info("In MainHandler")
    
    return render_template('recipeform.html', page_title="Search Recipes")      

def getRecipes(cuisine = "American", includeIngredients = '', intolerances = [], maxBudget=""):
    # max budget is set to a really high number if nothing is inputted --> 200 

    url_base = "https://api.spoonacular.com/recipes/complexSearch"

    api_key = "e2dc25e182cc4c00810492a29c63c459"

    #api_key = "d94fc0fb673c4cb2b61c29d83a4f9801"

    # turning the include ingredients list into a string 
    string_intolerances = ""
    if intolerances != []: 
        string_intolerances = string_intolerances + str(intolerances[0])
        intolerances.pop(0)
        for item in intolerances: 
            string_intolerances = string_intolerances + ", " + str(item)

    print(string_intolerances)

    query_string = {"cuisine": str(cuisine), "includeIngredients": str(includeIngredients), "intolerances": string_intolerances, "apiKey": api_key, "number": 10}
    # could set number to higher 

    url_request = url_base + "?" + urllib.parse.urlencode(query_string)
    print(url_request)


    headers = {"User-Agent":"Isha HCDE 310 Final (ishanara@uw.edu)"}
    req = urllib.request.Request(url_request,headers=headers)
    Data = urllib.request.urlopen(req).read()

    recipe_dictionary = json.loads(Data)
    #print(recipe_dictionary)

    recipe_dictionary = recipe_dictionary["results"]
    # get an the ID of each recipe in the recipe_dictionary 
    id_dictionary = {}
    
    # id_list = []

    for recipe in recipe_dictionary: 
        #id_list.append(recipe["id"])
        id = recipe["id"]
        title = recipe["title"]
        imageLink = recipe["image"]
        id_dictionary[id] = [title, imageLink]
    
    print(id_dictionary)

    if maxBudget == "":
        return id_dictionary 
    #return id_list
    else: 
        return(recipesWithinTheBudget(id_dictionary, maxBudget))



def getRecipes_safe(cuisine = "American", includeIngredients = '', intolerances = [], maxBudget=""):
        try:
                id_list_safe = getRecipes(cuisine, includeIngredients, intolerances, maxBudget)
        except(urllib.error.HTTPError) as c: 
                print("Error trying to retreive data")
                print("Reason:", c)                
        except(urllib.error.URLError)as e:
                print("Error trying to retreive data")
                print("Reason:", e)                 
        else:
                return(id_list_safe)


# will return a list
def recipesWithinTheBudget(id_dictionary, maxBudget): 

    #apikey = "d94fc0fb673c4cb2b61c29d83a4f9801"
    apikey = "e2dc25e182cc4c00810492a29c63c459"
    

    inBudget_recipies = {}


    ## pass in a single recipe ID 
    for id in id_dictionary.keys(): 
        
        # get the price of the recipe from the API (total the price of the ingredients)
        url = "https://api.spoonacular.com/recipes/{id}/priceBreakdownWidget.json".format(id = id)
        
        query = {"apiKey": apikey}

        request = url + "?" + urllib.parse.urlencode(query)

        headers = {"User-Agent":"Isha HCDE 310 Final (ishanara@uw.edu)"}
        req_price = urllib.request.Request(request,headers=headers)
        json_Data = urllib.request.urlopen(req_price).read()

        price_dictionary = json.loads(json_Data)
        cost_perserving = price_dictionary["totalCostPerServing"]      
        cost_perserving = cost_perserving/100
        # cost per serving is originally in cents 
        
        print(cost_perserving)
        
        title = id_dictionary[id][0]
        imageLink = id_dictionary[id][1]

        maxBudget = float(maxBudget)
        # if the recipe is less than the budget add it to the inBudget_recipies list 
        if cost_perserving <= maxBudget:
            #inBudget_recipies.append(id)
            inBudget_recipies[id] = [title, imageLink]

    print(inBudget_recipies)

    return inBudget_recipies

# make a dictionary with the ids corresponding to a list of [title, imagelink, ADD SOURCE URL]
def getRecipeUrl(recipe1): 
    # recipe1 is a dictioanary of the above structure 
    
    # need to add the recipe url --> seperate API call 

    for id in recipe1.keys(): 
        #apikey = "d94fc0fb673c4cb2b61c29d83a4f9801"
        apikey = "e2dc25e182cc4c00810492a29c63c459"
        
        # get the price of the recipe from the API (total the price of the ingredients)
        url = "https://api.spoonacular.com/recipes/{id}/information".format(id = id)
        
        query = {"apiKey": apikey}

        request_url = url + "?" + urllib.parse.urlencode(query)

        headers = {"User-Agent":"Isha HCDE 310 Final (ishanara@uw.edu)"}
        req_rec = urllib.request.Request(request_url,headers=headers)
        recipe_Data = urllib.request.urlopen(req_rec).read()

        rec_dictionary = json.loads(recipe_Data)

        url = rec_dictionary["sourceUrl"]
        recipe1[id].append(url)
    

    print(recipe1)
    return recipe1

@app.route("/gresponse")
def response_handler():
    cuisine = request.args.get('cuisine')
    print(cuisine)
    ingredients =  request.args.get('ingredients')
    print(ingredients)
    intolerances =  request.args.getlist('intolerances')
    print(intolerances)
    maxBudget = request.args.get('maxBudget')
    print(maxBudget)


    recipes1 = getRecipes(cuisine, ingredients, intolerances, maxBudget)
    
    # if the user hasnt entered in a cuisine set prompt to a message
    if cuisine == None: 
        return render_template('recipeform.html', page_title="Search Recipes", prompt = "Please Select a Cuisine to get Search Results!")   
   
    # if the list of IDS is blank set prompt to a message
    if recipes1 == {}:
        return render_template('recipeform.html', page_title="Search Recipes", prompt = "There were no results for your search please try a different one!")         


    # print out something about each recipe first
    return render_template('reciperesponse.html', 
            page_title = "Recipe Responses for %s"%cuisine, 
            #make a list of the attribute you want to print out about the recipe 
            recipes = getRecipeUrl(recipes1)

        )


if __name__ == "__main__":
    # Used when running locally only. 
	# When deploying to Google AppEngine, a webserver process will
	# serve your app. 
    app.run(host="localhost", port=8080, debug=True)