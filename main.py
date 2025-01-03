import rebound #integrator
import numpy as np 
from nicegui import ui, app #nicegui framework
import plotly.graph_objects as go #plot in ploty
import os #for images
from astropy.time import Time 
from datetime import datetime, timedelta, timezone

@ui.page('/b')  
class GalileanMoonApp:
    
    def __init__(self):
        self.sim = None
        self.fig = None
        self.particles = None
        self.plot = None
        self.cloudy = False
        self.white = False
        self.init_images()
        self.dt= 0.05
        self.jump=12
        self.time_label=None
        self.date= None


    def toggle_background(self,enabled:bool):
        """Change background to white/ back to black

        Args:
            enabled (bool): White or Black
        """
        if enabled:
            self.white=True
            self.integrator(self.date.value)
        else:
            self.white=False
            self.integrator(self.date.value)
    def toggle_clouds(self,enabled: bool):
        """ Add in clouds

        Args:
            enabled (bool): clouds or no clouds
        """
        if enabled:
            self.cloudy= True
        
        else:
            self.cloudy=False
            


    #creating simulation/integrator objects     
    
    def create_system(self):
        self.sim = rebound.Simulation()
        self.sim.units = ('day', 'AU', 'mjupiter') #units for time distance and mass
        Jupiter= self.sim.add(m=1.)   #Time   2460510.229769, 2024-Jul-18 17:30   GMT       
        Io= self.sim.add(m=4.7e-5,
                    a=0.002818623004285437,
                    e=0.004079857301041492,
                    inc=0.03804794156031389, 
                    Omega=-0.38893968645378835, 
                    omega=4.864278675471462,
                    f=5.682659640352345)# mass, semi-major axis, eccentricity, inclination, TA, 
        Europa=self.sim.add(m=2.5e-5,
                    a=0.004487980554823025,
                    e=0.00974154548746722, 
                    inc=0.039931236158043795, 
                    Omega=-0.5877637812980877, 
                    omega=1.9223130235217791,
                    f=5.988730260389364)
        Ganymede= self.sim.add(m=7.8e-5,
                        a=0.007152056499240089,
                        e=0.0021576877565359837,
                        inc=0.04066564317570219, 
                        Omega=-0.35600170771928724, 
                        omega=6.192000690608995, 
                        f=4.78191323984481)
        Callisto= self.sim.add(m=5.7e-5, 
                        a=0.012580426532110564, 
                        e=0.007542503282625529, 
                        inc=0.03403046222325111, 
                        Omega=-0.40443704900755467, 
                        omega=0.5510916429261528, 
                        f=2.4575789851499366)


        self.sim.integrator = "whfast" #whfast integrator
        self.sim.dt =self.dt.value #by the day
        return self.sim

    def clouds(self):
        """putting clouds on the screen
        """
        if np.random.randint(0,20) < 1:
            self.fig.update_layout(
            images=[
                dict(
                source= self.cloud_image,
                xref="x", yref="y",
                x=self.particles[0].x, y=self.particles[0].z,
                sizex=.0555, sizey=.0555,
                xanchor="center", yanchor="middle"
                ),
                ]
            )
        self.plot.update()


    def get_distance(self, particle):
        """Measuring distance of moons to jupiter (will be displayed when hovering over moon)

        Args:
            particle (_class_): The particle number (1-4 associated with each moon)

        Returns:
            _int_: returns distance in in Djup
        """
        distance = self.particles[particle].x- self.particles[0].x
        Jdistance= distance/0.000954559041 #divide by AUs in Jupiter diameter
        r_distance= abs(round(Jdistance, 5))
        return r_distance #returning Daimeters of Jupiter as a distance.

    def init_images(self):
        app.add_static_files(os.path.join(os.getcwd(), 'figs'), 'figs')
        self.io_image = os.getcwd() + '/figs/io.png'
        self.europa_image = os.getcwd() + '/figs/europa.png'
        self.gany_image = os.getcwd() + '/figs/ganymede.png'
        self.callisto_image = os.getcwd() + '/figs/callisto.png'
        self.jupiter_image = os.getcwd() + '/figs/Jupiter.png'
        self.cloud_image = os.getcwd() + '/figs/clouds.jpeg'
    
     
    def integrator(self, entry):
        """ Takes in time value and integrates simulation to that value

        Args:
            value (_type_):
        """
        try:
            t=Time(entry, format="iso" )
        except ValueError:
            ui.notify('Improper date and time ex. (2024-07-18 22:30:30.55) ')
            
        time= (t.jd - 2460510.229769)
        self.sim.integrate(time)   
        self.sim.move_to_com()
        self.particles = self.sim.particles
        
        #ordering the planets (transit in front vs behind Jupiter)
        zorders=np.linspace(0,4,5)
        zorders2=['','','','','']
        for i in zorders:
            if -0.000265 <= self.particles[int(i)].x <= 0.000265 and self.particles[int(i)].z >=0:
                zorders2[int(i)]= "below"
            else:
                zorders2[int(i)]="above"
        for i in zorders:
            if self.particles[int(i)].z >=0:
                zorders[int(i)]= 3
            else:
                zorders[int(i)]=1
                
        self.fig.data = []
        io=self.fig.add_trace(go.Scatter(
        x=[self.particles[1].x],
        y=[self.particles[1].z],
        mode='markers',
        name='Io',
        text=[f"Io, the distance is {self.get_distance(1)} Dj"],
        hoverinfo='text',
        zorder=int(zorders[1])
        ))
        Europa=self.fig.add_trace(go.Scatter(
        x=[self.particles[2].x],
        y=[self.particles[2].z],
        mode='markers',
        name='Europa',
        text=[f"Europa, the distance is {self.get_distance(2)} Dj"],
        hoverinfo='text',
        zorder=int(zorders[2])
        ))
        Ganymede=self.fig.add_trace(go.Scatter(
            x=[self.particles[3].x],
            y=[self.particles[3].z],
            mode='markers',
            name='Ganymede',
            text=[f"Ganymede, the distance is {self.get_distance(3)} Dj"],
            hoverinfo='text',
            zorder=int(zorders[3])
        ))
        
        Callisto=self.fig.add_trace(go.Scatter(
            x=[self.particles[4].x],
            y=[self.particles[4].z],
            mode='markers',
            name='Callisto',
            text=[f"Callisto, the distance is {self.get_distance(4)} Dj"],
            hoverinfo='text',
            zorder=int(zorders[4])
        ))
        
        Jupiter=self.fig.add_trace(go.Scatter(
            x=[self.particles[0].x],
            y=[self.particles[0].z],
            mode='markers',
            name='Jupiter',
            text=['Jupiter'],
            hoverinfo='text',
            zorder=2
        ))
        self.fig.update_layout(
            images=[
                dict(
                    source= self.jupiter_image,
                    xref="x", yref="y",
                    x=self.particles[0].x, y=self.particles[0].z,
                    sizex=.000955*2, sizey=.000955*2,
                    xanchor="center", yanchor="middle"
                ),
                dict(                
                    source= self.io_image,
                    xref="x", yref="y",
                    x=self.particles[1].x, y=self.particles[1].z,
                    sizex=0.000245, sizey=0.000245,
                    xanchor="center", yanchor="middle",
                    layer=zorders2[1],
                    visible = True
                    
                ),
                dict(                
                    source=self.europa_image,
                    xref="x", yref="y",
                    x=self.particles[2].x, y=self.particles[2].z,
                    sizex=0.00021, sizey=0.00021,
                    xanchor="center", yanchor="middle",
                    visible = True,
                    layer=zorders2[2]
                ),
                dict(                
                    source=self.gany_image,
                    xref="x", yref="y",
                    x=self.particles[3].x, y=self.particles[3].z,
                    sizex=0.00035, sizey=0.00035,
                    xanchor="center", yanchor="middle",
                    visible = True,
                    layer=zorders2[3]
                ),
                dict(                
                    source=self.callisto_image,
                    xref="x", yref="y",
                    x=self.particles[4].x, y=self.particles[4].z,
                    sizex=0.00032, sizey=0.00032,
                    xanchor="center", yanchor="middle",
                    visible = True,
                    layer= zorders2[4]
                )
            ],
            title='Galilean Moons'
        )
        self.fig.update_layout(
            xaxis=dict(
                showline=False,  # Hide x-axis line
                showticklabels=False,  # Hide x-axis labels
                zeroline=False,  # Hide x-axis zeroline
                showgrid=False  # Hide x-axis gridlines
            ),
            yaxis=dict(
                showline=False,  # Hide y-axis line
                showticklabels=False,  # Hide y-axis labels
                zeroline=False,  # Hide y-axis zeroline
                showgrid=False  # Hide y-axis gridlines
            ),
            plot_bgcolor='black',  # Set plot background color to black
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper
            showlegend=False
        )
        if self.white:
            self.fig.layout.update(plot_bgcolor='white')
        self.fig.layout.update(yaxis_range = [-.020,.020])
        self.fig.layout.update(xaxis_range = [-.020,.020])
        self.fig.update_traces(marker=dict(size=.0010))
        self.fig.update_layout(modebar_remove=[
            'zoom2d', 
            'pan', 
            'lasso', 
            'select',
            'zoomout',
            'zoomin',
            'autoscale',
            'resetScale',
            'displaylogo',
            ])
        if self.cloudy:
            self.clouds()
        with self.time_label:
            self.time_label.text=str(entry) +f' UTC'
        self.time_label.update()
        with self.date:
            self.date.value= str(entry)
        self.date.update()
            
        
        self.plot.update()


    def zooms(self, zoom):
        """ zoom in and out create buttons for zoom
    Args:
        zoom (_int_): zoom x100 eg. 1= 100x zoom 
    Returns:
        
    """
        a=.020/zoom
        self.fig.layout.update(yaxis_range = [-a,a]) 
        self.fig.layout.update(xaxis_range = [-a,a])
        self.plot.update()
    def time_jump(self, time_label):
        time_change = timedelta(hours=self.jump.value) 
        date_format = '%Y-%m-%d %H:%M:%S'
        date_obj = datetime.strptime(time_label, date_format)
        return str(time_change + date_obj) 
    
       
      
    def run(self):
        self.init_images()
        ui.query('body').style(f'background-color:#e9edf0') #initial look 
        with ui.row().classes('w-full items-center'):
            ui.label('Galilean Moon Simulator').tailwind.font_family(
                'mono').text_color('black-600').font_size('5xl').font_weight('bold') #title

            result = ui.label().classes('mr-auto')
            #menu button and options
            with ui.button(icon='menu'):
                with ui.menu() as menu:
                    ui.label('Clouds')
                    switch_clouds= ui.switch( on_change=lambda e: self.toggle_clouds(e.value))
                    ui.label('White background')
                    switch_background = ui.switch(on_change=lambda e: self.toggle_background(e.value))
                    self.dt= ui.number(label = 'Timestep in Days', value=.05, min=0,step=0.001,
                                precision= 3)
                    self.jump= ui.number(label = "Time Jump in Hours",
                                    value=12, min=-1000, max=1000, step=1, precision=1)

        self.create_system()
        self.fig = go.Figure()
        self.fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        self.plot = ui.plotly(self.fig).classes('w-full h-full')
        
        utc=datetime.now(timezone.utc).replace(microsecond=0).replace(tzinfo=None)
        utc_string= str(utc)
        with ui.row():
            with ui.input('Date', value= utc_string.replace('T', ' ')) as self.date:
                with ui.menu().props('no-parent-event') as menu:
                    with ui.date().bind_value(self.date):
                        with ui.row().classes('justify-end'):
                            ui.button('Close', on_click=menu.close).props('flat')
                with self.date.add_slot('append'):
                    ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
            self.time_label=ui.label()
            """ move state forward by 12 hours
            Args:
            time_label (_str_): _time currently integrated to_
            Returns:
            _str_: _returns a string thats then used in the integrator to push forward the step_
            """
            ui.button('Enter', on_click=lambda: self.integrator(self.date.value))
        
            ui.button('Time Jump', on_click=lambda: 
                self.integrator(self.time_jump(self.time_label.text.replace(' UTC',''))))

        with ui.row():
            ui.button('100x', on_click=lambda: self.zooms(1))
            ui.button('200x', on_click =lambda: self.zooms(2))
            ui.button('300x',  on_click =lambda: self.zooms(3))
            ui.button('400x',  on_click =lambda: self.zooms(4))

        
        self.integrator(str(utc))
        
@ui.page("/")
def main():
    application = GalileanMoonApp()
    application.run()
main()
ui.run()
