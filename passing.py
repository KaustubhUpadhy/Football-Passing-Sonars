from statsbombpy import sb
# comp =sb.competitions()    # Assigns all the free available competetions to the object
#comp.to_csv("competitions.csv", index=False)
#match = sb.matches(16,2)
#match.to_csv("match.csv")
MATCH_ID = 18244
Team = "Real Madrid"
passes = sb.events(match_id= MATCH_ID, split= True, flatten_attrs=False)["passes"]
passes = passes[passes["team"]==Team]
df = passes[['pass','player']]
#df.to_csv("pass.csv",index=False)
#print(df.iloc[0]['pass'])
df['angle']= [df['pass'][i]['angle'] for i in df.index]
df['length']=[df['pass'][i]['length']for i in df.index]

import pandas as pd
import numpy as np

df['angle_bin']= pd.cut(
    df['angle'],bins=np.linspace(-np.pi,np.pi,21),
    labels = False, include_lowest= True
)

#average length
sonar_df=df.groupby(["player","angle_bin",], as_index=False)
sonar_df=sonar_df.agg({"length":"mean"})

#counting passes for each angle bin
pass_amt=df.groupby(["player","angle_bin"]).size().to_frame(name='amount').reset_index()

#concatenating the data
sonar_df = pd.concat([sonar_df,pass_amt["amount"]],axis = 1)

#extracting coordinates
passes["x"],passes["y"] = zip(*passes["location"])

average_location = passes.groupby('player').agg({'x':['mean'],'y':['mean']})
average_location.columns =['x','y']

sonar_df= sonar_df.merge(average_location,left_on="player",right_index=True)

lineups = sb.lineups(match_id=MATCH_ID)[Team]
lineups['starter']=[
    lineups['positions'][i][0]['start_reason']=='Starting XI'
    if lineups ['positions'][i]!=[]
    else None
    for i in range (len(lineups))
]
lineups=lineups[lineups['starter']==True]

startingXI =lineups['player_name'].to_list()

sonar_df = sonar_df[sonar_df['player'].isin(startingXI)]

from mplsoccer import Pitch
import matplotlib.pyplot as plt
import matplotlib.patches as pat

fig ,ax = plt.subplots(figsize=(20, 12),constrained_layout=False, tight_layout=True)
fig.set_facecolor('#0e1117')
ax.patch.set_facecolor('#0e1117')
pitch = Pitch(pitch_type='statsbomb', pitch_color='#0e1117', line_color='#c7d5cc')
pitch.draw(ax=ax)

for player in startingXI:
        for _, row in sonar_df[sonar_df.player == player].iterrows():
                degree_left_start = 198
                
                color = "gold" if row.amount < 3 else "darkorange" if row.amount < 5 else '#9f1b1e'

                n_bins = 20
                degree_left = degree_left_start +(360 / n_bins) * (row.angle_bin)
                degree_right = degree_left - (360 / n_bins)
                
                pass_wedge = pat.Wedge(
                        center=(row.x, row.y),
                        r=row.length*0.16, # scaling the sonar segments
                        theta1=degree_right,
                        theta2=degree_left,
                        facecolor=color,
                        edgecolor="black",
                        alpha=0.6
                )
                ax.add_patch(pass_wedge)

realmadrid_dict = {
        "Carlos Henrique Casimiro":"Casemiro",
        "Cristiano Ronaldo dos Santos Aveiro":"Cristiano Ronaldo",
        "Daniel Carvajal Ramos":'Dani Carvajal',
        "Francisco Román Alarcón Suárez":'Isco',
        "Karim Benzema":"Karim Benzema",
        "Keylor Navas Gamboa": "Keylor Navas",
        "Luka Modrić": "Modric",
        "Marcelo Vieira da Silva Júnior":"Marcelo",
        "Raphaël Varane":"Varane",
        "Sergio Ramos García":"Sergio Ramos",
        "Toni Kroos":"Toni Kroos"
}
for _, row in average_location.iterrows():
        if row.name in startingXI:
            annotation_text = realmadrid_dict[row.name]

            pitch.annotate(
                annotation_text,
                xy=(row.x, row.y-4.5),
                c='white',
                va='center',
                ha='center',
                size=9,
                fontweight='bold',
                ax=ax
            )

ax.set_title(f"Real Madrid vs Juventus: Champions League 2016/17 Final \n Passing Sonars for Real Madrid's Starting XI", fontsize =18,color="r",fontfamily="Monospace", fontweight='bold', pad=-8 )
pitch.annotate('Sonar color corresponds to pass frequency (dark = more)',xy=(0.5, 0.01), xycoords='axes fraction', fontsize=10, color='white', ha='center', va='center', fontfamily="Monospace", ax=ax)
plt.show()