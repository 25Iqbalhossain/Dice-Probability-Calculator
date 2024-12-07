import streamlit as st
import plotly.graph_objects as go


def cumulative_probabilities(dice_sides, target_number, max_rolls=10, cache={}):
   
    if (max_rolls, target_number) in cache:
        return cache[(max_rolls, target_number)]

  
    probabilities = [[0] * (target_number + 2) for _ in range(max_rolls + 1)]  # Adjust array size for +1 case

    for i in range(1, dice_sides + 1):
        if i <= target_number:
            probabilities[1][i] = 1 / dice_sides

 
    for roll in range(2, max_rolls + 1):
        for total in range(1, target_number + 1):
            for face in range(1, dice_sides + 1):
                if total - face > 0:
                    probabilities[roll][total] += probabilities[roll - 1][total - face] / dice_sides


    win_probability = sum(probabilities[roll][target_number] for roll in range(1, max_rolls + 1))

    partial_win_probability = 0
    for roll in range(1, max_rolls + 1):
        if 1 <= target_number - 1 < len(probabilities[roll]):
            partial_win_probability += probabilities[roll][target_number - 1]
        if 1 <= target_number + 1 < len(probabilities[roll]):
            partial_win_probability += probabilities[roll][target_number + 1]

  
    cache[(max_rolls, target_number)] = (win_probability, partial_win_probability)

    return win_probability, partial_win_probability


def cumulative_probabilities_cdf(dice_sides, target_number, max_rolls=10):
    probabilities = [[0] * (target_number + 1) for _ in range(max_rolls + 1)]

   
    for i in range(1, min(dice_sides, target_number) + 1):
        probabilities[1][i] = 1 / dice_sides

   
    for roll in range(2, max_rolls + 1):
        for total in range(1, target_number + 1):
            for face in range(1, min(dice_sides, total) + 1):
                probabilities[roll][total] += probabilities[roll - 1][total - face] / dice_sides

    
    cdf = [sum(probabilities[roll][i] for roll in range(1, max_rolls + 1)) for i in range(target_number + 1)]
    return cdf

def plot_cdf_with_plotly(dice_sides, max_target, max_rolls):
    cdf_values = [cumulative_probabilities_cdf(dice_sides, target, max_rolls)[-1] for target in range(1, max_target + 1)]
    fig = go.Figure(data=go.Scatter(x=list(range(1, max_target + 1)), y=cdf_values, mode='lines+markers'))
    fig.update_layout(
        title=f'Cumulative Distribution Function up to Target {max_target}',
        xaxis_title='Target Score',
        yaxis_title='Cumulative Probability',
        margin=dict(l=40, r=40, t=40, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)




st.sidebar.title("Dice Probability Calculator")

st.sidebar.number_input("Target number", min_value=1, key="target_number", value=25)
st.sidebar.select_slider("Number of sides on the dice", options=[4, 6, 8, 10, 12, 20], value=6, key="dice_sides")
st.sidebar.slider("Maximum number of rolls", min_value=1, max_value=100, key="max_rolls", value=10)

dice_sides = st.session_state.dice_sides
target_number = st.session_state.target_number
max_rolls = st.session_state.max_rolls

st.sidebar.caption(f"Maximum possible target number is {dice_sides * max_rolls}")

if target_number > dice_sides * max_rolls or target_number < 1:
    st.error(
        f"The target number should be between 1 and the maximum possible score ({dice_sides * max_rolls}) for a {dice_sides}-sided dice with {max_rolls} rolls."
    )
    st.stop()

win_probability, partial_win_probability = cumulative_probabilities(dice_sides, target_number, max_rolls)
loss_probability = 1 - win_probability - partial_win_probability

st.header("Chances of Hitting Target Scores with Rolls")
plot_cdf_with_plotly(dice_sides, target_number, max_rolls)

col1, col2, col3 = st.columns(3)
col1.metric("Win Probability", f"{win_probability:.6f}")
col2.metric("Partial Win Probability", f"{partial_win_probability:.6f}")
col3.metric("Loss Probability", f"{loss_probability:.6f}")
