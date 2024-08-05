import json

# JSON string, note the double quotes
json_string = """
{ 
    "Case Study": "The property in question is a medium-sized 150m real estate located in the upscale 5th Settlement district of New Cairo, Egypt. It has been recently renovated and sits in proximity to several commercial and leisure establishments in the region. There's also easy access to public transportation. The recent promotional campaign saw the utilization of both traditional and digital marketing strategies, including the use of social media platforms like Facebook and Twitter to increase the property's visibility to potential buyers or tenants. High-quality images and concise but compelling listing descriptions proved effective in generating inquiries and property viewings.", 
    "Target Audience": "The target audience includes affluent professionals and families within the ages of 30-55 who value convenience and upscale living. Also, real estate investors looking for properties with good ROI potential in high-end markets are also targeted.", 
    "Pros": "The property's location in a high-end neighborhood adds to its appeal and value. Its proximity to commercial and leisure establishments also makes it an attractive choice for potential homeowners or renters who value convenience. The promotional campaign's success in generating interest and inquiries demonstrates the effectiveness of the marketing tactics employed.", 
    "Cons": "A potential downside would be the property's price, which may be on the higher end, given its location and size. This may discourage price-sensitive buyers or renters. The reliance on digital marketing might also overlook potential buyers not active on social media or those who prefer traditional methods of property search.", 
    "Facebook Hashtags": "#5thSettlementProperty #LuxuryLiving #RealEstateEgypt #PropertyInvestmentEgypt", 
    "Twitter Hashtags": "#5thSettlementHomes #EgyptRealEstate #PropertyFindEgypt"
}
"""

# Parse the JSON string into a Python dictionary
data = json.loads(json_string)

# Accessing individual items
case_study = data['Case Study']
target_audience = data['Target Audience']
pros = data['Pros']
cons = data['Cons']
facebook_hashtags = data['Facebook Hashtags']
twitter_hashtags = data['Twitter Hashtags']

# Print some data
print("Case Study:", case_study)
print("Target Audience:", target_audience)
print("Pros:", pros)
print("Cons:", cons)
print("Facebook Hashtags:", facebook_hashtags)
print("Twitter Hashtags:", twitter_hashtags)