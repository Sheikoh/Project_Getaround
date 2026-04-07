Project GetAround

This project aims at improving an application to rent cars based on two considerations:
1 - Rentals that closely follow one another can be impacted if the first one is late. How beneficial would it be to impose a delay between rentings ?
2 - The renters have no basis to set their prices. What would be a way to optimise their pricing ?

**1 - Improvement through delays**

In this part, we use data analysis to estimate the number of rentals impacted by the lateness of the previous users, and the number of issues that would be solved by implementing a mandatory delay between two rentals, up to 720 minutes. 

The results are served on a streamlit dashboard and accessible at the following adress:

https://huggingface.co/spaces/Sheyko/Dashboard_getaround

The code is contained in the Dashboard folder.

**2 - Pricing optimisation**

The second part recommends a price point for a rental based on the vehicule informations. It can be accessed by a post request at the following endpoint.

https://sheyko-getaround-api.hf.space/predict

The prediction endpoint assumes that the data was already formatted to be compliant to the expected column formatting.

The code associated with the API in contained in the API folder.