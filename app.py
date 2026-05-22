import streamlit as st
import numpy as np
import matplotlib.pyplot as plt 

ESTATE_TYPES = {
    "small":  {"points": 1, "size_range": (10_000, 50_000)},
    "medium": {"points": 2, "size_range": (51_000, 150_000)},
    "large":  {"points": 3, "size_range": (151_000, 400_000)},
}
class Developer:
    def __init__(self,name,build_rate):
        self.name = name
        self.build_rate = build_rate
        self.build_rate_log = []
        self.portfolio = []
    
    def acquire(self, avaible_plots):
        points = int(self.build_rate * 6)
        total_aquired = 0

        while points > 0 and avaible_plots > 10_000:
            if points >= 3:
                estate_type = np.random.choice(['small','medium','large'])
            elif points == 2:
                estate_type = np.random.choice(['small', 'medium'])
            else:
                estate_type = 'small'

            #losuj rozmiar
            size_min, size_max = ESTATE_TYPES[estate_type]['size_range']
            size = np.random.randint(size_min, size_max)

            #stwórz osiedle i dodaj do portfela
            estate = Estate(estate_type, size)
            self.portfolio.append(estate)


            # zaktualizuj liczniki
            points -= ESTATE_TYPES[estate_type]['points']
            total_aquired += size
            avaible_plots -= size

        return total_aquired
    
    def log_state(self):
        self.build_rate_log.append(self.build_rate)

    def portfolio_value(self):
        return sum([e.value for e in self.portfolio])

class LandBank:
    def __init__(self, available_plots):
        self.available_plots = available_plots
        self.history = []
        self.available_plots_max = available_plots

    def develop(self, amount):
        self.available_plots = int(max(0,self.available_plots - amount))

    def log_state(self):
        self.history.append(self.available_plots)
    
    def release_plots(self,rate):
        self.available_plots = int(min(self.available_plots * (1 + rate), self.available_plots_max))

class Estate:
    def __init__(self,type, value, age=0):
        self.type = type #small, medium, large
        self.value = value 
        self.age = 0

    def depreciate(self):
        self.value = self.value * 0.98

    def birthday(self):
        self.age += 1


st.title('🏢 Concrete vs. Green: Developer Expansion Simulator')
st.markdown("### *An interactive tool tracking the transformation of urban green spaces*")

st.sidebar.header("Developer's parameters")

domdev_rate = st.sidebar.slider("DomDevelopment build rate", 0.0, 1.0, 0.3)
echo_rate = st.sidebar.slider("EchoInvestments build rate", 0.0, 1.0, 0.1)
atal_rate = st.sidebar.slider("Atal build rate", 0.0, 1.0, 0.05)

st.sidebar.header("Simulation parameters")
n_rounds = st.sidebar.slider("Number of rounds", 10, 200, 50)
regen_rate = st.sidebar.slider("Plot regeneration rate", 0.0, 0.5, 0.1)


st.sidebar.info("""
**Estate size reference:**
- Small: 5-15 ha
- Medium: 15-50 ha
- Large: 50+ ha (e.g. Wilanów, Warsaw ~170 ha)
""")


domDev = Developer('DomDevelopment', domdev_rate)
echo = Developer('EchoInvestments', echo_rate)
atal = Developer('Atal', atal_rate)

land = LandBank(163425000)# m^2
developers = [domDev,echo,atal]
n_developers=len(developers)