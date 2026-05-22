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
        self.portfolio_log = []
    
    def acquire(self, avaible_plots, land, enable_payoffs):
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
            if enable_payoffs:
                green_ratio = land.available_plots/land.available_plots_max
            else:
                green_ratio = 1.0
            estate = Estate(estate_type, int(size * green_ratio))
            self.portfolio.append(estate)

            # zaktualizuj liczniki
            points -= ESTATE_TYPES[estate_type]['points']
            total_aquired += size
            avaible_plots -= size

        return total_aquired
    
    def log_state(self):
        self.build_rate_log.append(self.build_rate)
        self.portfolio_log.append(self.portfolio_value())

    def apply_retention(self, land):
        new_portfolio = []
        for e in self.portfolio:
            if e.age < 100:
                new_portfolio.append(e)
            else:
                land.available_plots = min(
                    land.available_plots + e.size,
                    land.available_plots_max
                )
        self.portfolio = new_portfolio
    
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
    
class Estate:
    def __init__(self,type, size, age=0):
        self.type = type #small, medium, large
        self.value = size 
        self.size = size
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
st.sidebar.header("City renewal parameters")
release_amount = st.sidebar.slider("Release amount (m²)", 10_000,1_200_000,100_000)
release_freq = st.sidebar.slider("Release frequency", 0.2, 1.0, 0.4)
enable_retention =st.sidebar.checkbox("Enable 100-year retention", value=False)
enable_payoffs = st.sidebar.checkbox("Enable green ratio penalty", value=False)

st.sidebar.info("""
**Estate size reference:**
- Small: 5-15 ha
- Medium: 15-50 ha
- Large: 50+ ha (e.g. Wilanów, Warsaw ~170 ha)
""")


domDev = Developer('Dom Development', domdev_rate)
echo = Developer('Echo Investments', echo_rate)
atal = Developer('Atal', atal_rate)

land = LandBank(24_000_000)# m^2
developers = [domDev,echo,atal]
n_developers=len(developers)

for i in range(n_rounds):
    for a in developers:
        aquired = a.acquire(land.available_plots, land, enable_payoffs)
        land.develop(aquired)

    if np.random.random() < release_freq:
        land.available_plots =min(
            land.available_plots + release_amount,
            land.available_plots_max
        )
    land.log_state()

    for g in developers:
        if enable_retention:
            g.apply_retention(land)
        for p in g.portfolio:
            p.depreciate()
            p.birthday()
        g.log_state()

fig, ax = plt.subplots()
ax.plot(range(n_rounds), land.history, label="Available plots")
ax.set_xlabel("Rounds")
ax.set_ylabel("Available plots (m²)")
ax.set_title("Land Bank over time")
ax.legend()

st.pyplot(fig)

fig2, ax2 = plt.subplots()
for dev in developers:
    ax2.plot(range(n_rounds), dev.portfolio_log, label=dev.name)
ax2.set_xlabel("Rounds")
ax2.set_ylabel("Portfolio value (m²)")
ax2.set_title("Developer portfolio value over time")
ax2.legend()

st.pyplot(fig2)

st.subheader("🏆 Final Rankings")
cols = st.columns(3)

sorted_devs = sorted(developers, key=lambda d: d.portfolio_value(), reverse=True)

for i, dev in enumerate(sorted_devs):
    cols[i].metric(
        label=dev.name,
        value=f"{dev.portfolio_value():,.0f} m²"
    )