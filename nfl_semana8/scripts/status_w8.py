# -*- coding: utf-8 -*-
# Reporte final de lesiones de la semana 8 (viernes 30-oct-2026), capturado a mano desde reportes de equipos y medios.
# nflverse todavía no tenía las designaciones del viernes; esto las reemplaza. CHI-SEA juega el lunes: su reporte final sale el sábado.
OUT = {  # jugador: (equipo, motivo)
    'Olaivavega Ioane': ('BAL', 'G · rodilla'),
    'Tyjae Spears': ('TEN', 'RB · rodilla'), 'Carnell Tate': ('TEN', 'WR · hombro'),
    'KaVontae Turpin': ('DAL', 'WR · costillas'),
    'Anthony Gould': ('IND', 'WR · conmoción'),
    'Max Mitchell': ('NYJ', 'T · lesión'),
    'Brian Robinson Jr.': ('ATL', 'RB · isquiotibial'),
    'Emeka Egbuka': ('TB', 'WR · pie'),
    'Kayode Awosika': ('LAC', 'G · peroné'), 'Brenen Thompson': ('LAC', 'WR · cuádriceps/isquiotibial'),
    'RJ Harvey': ('DEN', 'RB · rodilla'),
    'Kadyn Proctor': ('MIA', 'OL · conmoción'),
    'DeVonta Smith': ('PHI', 'WR · isquiotibial'), 'Dontayvion Wicks': ('PHI', 'WR · tobillo'), 'Britain Covey': ('PHI', 'WR · rodilla'),
}
QUESTIONABLE = {  # jugador: (equipo, nota)
    'Adam Randall': ('BAL', 'RB'),
    'DJ Moore': ('BUF', 'hombro; limitado'), 'Dalton Kincaid': ('BUF', 'pecho; limitado'), 'Spencer Brown': ('BUF', 'T · espalda'),
    'Calvin Ridley': ('TEN', 'cadera'),
    'George Pickens': ('DAL', 'hombro/isquiotibial; el coach espera que juegue'), 'Luke Schoonmaker': ('DAL', 'ingle'),
    'Drew Ogletree': ('IND', 'rodilla; un reporte dice que se perderá el juego'),
    'Jakobi Meyers': ('JAX', 'isquiotibial/tobillo; no practicó el viernes'),
    'Jack Bech': ('LV', 'antebrazo'), 'Jackson Powers-Johnson': ('LV', 'G · enfermedad'),
    'Breece Hall': ('NYJ', 'cuádriceps; regresaría tras perderse S4-S7'), 'Dylan Parham': ('NYJ', 'G · rodilla'),
    'Tytus Howard': ('CLE', 'T · conmoción; no practicó en toda la semana'),
    'Ben Skowronek': ('PIT', 'pantorrilla'),
    'Olamide Zaccheaus': ('ATL', ''), 'Beaux Collins': ('ATL', 'cadera'),
    'Kenny Gainwell': ('TB', 'cadera'), 'Luke Goedeke': ('TB', 'T · pantorrilla'),
    'Colby Parkinson': ('LA', 'costilla'), 'Coleman Shelton': ('LA', 'C · cadera'),
    'Jaylen Waddle': ('DEN', 'pecho'), 'Garett Bolles': ('DEN', 'T · cadera'),
    'A.J. Brown': ('NE', 'tobillo/rodilla; no practicó jue-vie; se decide el sábado'), 'TreVeyon Henderson': ('NE', 'enfermedad'),
    'Treylon Burks': ('WAS', ''), 'John Bates': ('WAS', ''),
}
CLEARED = {  # confirmados sin designación / regresan
    'Lamar Jackson': ('BAL', 'Practicó completo mié-vie; sin designación. Regresa tras 3 juegos fuera (esguince alto).'),
    'Michael Wilson': ('ARI', 'El coach lo dio por listo (costillas); fuera del reporte.'),
    'Jeremiyah Love': ('ARI', 'Se espera que juegue (tobillo).'),
    'Tyler Warren': ('IND', 'El coach confirmó que juega.'),
    'Ladd McConkey': ('LAC', 'Superó el protocolo de conmoción; sin designación.'),
    "Tre' Harris": ('LAC', 'Fuera del reporte; juega.'),
    'Rashee Rice': ('KC', 'Regresa de lesión de isquiotibial (no juega desde la S4).'),
    'Travis Kelce': ('KC', 'Practicó completo el viernes; sin designación.'),
    'Saquon Barkley': ('PHI', 'Regresó a practicar el viernes; sin designación.'),
    'Dallas Goedert': ('PHI', 'Practicó completo; sin designación.'),
    'Jayden Daniels': ('WAS', 'Practicó completo; sin designación.'),
    'Puka Nacua': ('LA', 'Descanso el viernes; sin designación.'),
    "Ja'Marr Chase": ('CIN', 'Sin designación.'),
    'Jahmyr Gibbs': ('DET', 'Practicó completo el viernes; sin designación.'),
    'Amon-Ra St. Brown': ('DET', 'Practicó completo el viernes; sin designación.'),
    'Aaron Jones Sr.': ('MIN', 'Rodilla; sin designación, se espera que juegue.'),
    'Drake Maye': ('NE', 'Fuera del reporte.'),
}
PENDING_TEAMS = {'CHI', 'SEA'}  # lunes: reporte final el sábado
PENDING_NOTES = {
    'Rashid Shaheed': ('SEA', 'No practicó el jueves (rodilla). Reporte final el sábado.'),
    'Velus Jones Jr.': ('SEA', 'No practicó el jueves (isquiotibial). Reporte final el sábado.'),
    'Jaxon Smith-Njigba': ('SEA', 'Descanso el jueves (no es lesión). Reporte final el sábado.'),
}
RETURNING = {'Lamar Jackson', 'Rashee Rice', 'Ladd McConkey', "Tre' Harris", 'Jeremiyah Love', 'Tyler Warren', 'Breece Hall', 'Joe Alt'}
QB_STARTER = {'BAL': 'Lamar Jackson'}  # el resto: titular del último juego
# Titulares de OL (los 5 con más snaps) que no jugarían en la S8: 1 = fuera (o fuera del equipo), 0.5 = duda.
OL_OUT_NOW = {
    'BAL': (1, 'G Olaivavega Ioane fuera'), 'BUF': (0.5, 'RT Spencer Brown en duda'), 'TEN': (0, ''), 'CIN': (0, ''),
    'ARI': (1, 'LT Paris Johnson en reserva'), 'DAL': (1, 'T.J. Bass fuera de la alineación desde la S5'), 'MIN': (0, ''), 'DET': (0, ''),
    'IND': (1, 'Quenton Nelson traspasado a SEA'), 'JAX': (1, 'RT Anton Harrison en reserva'), 'LV': (0.5, 'G Jackson Powers-Johnson en duda'),
    'NYJ': (0, ''), 'CLE': (1, 'RT Tytus Howard (conmoción, no practicó)'), 'PIT': (0, ''), 'ATL': (0, ''), 'TB': (0.5, 'RT Luke Goedeke en duda'),
    'LAC': (1, 'LT Rashawn Slater en reserva (Joe Alt regresa)'), 'LA': (0.5, 'C Coleman Shelton en duda'), 'KC': (0, ''),
    'DEN': (0.5, 'LT Garett Bolles en duda'), 'NE': (1, 'G Alijah Vera-Tucker en reserva'), 'MIA': (1, 'OL Kadyn Proctor fuera'),
    'PHI': (1, 'C Cam Jurgens traspasado a BAL'), 'WAS': (0, ''), 'CHI': (0, ''),
    'SEA': (1.5, 'Christian Haynes traspasado a MIA; LT Charles Cross (tobillo) no practicó el jueves'),
}
FUENTES = [
    ('Ravens/Bills (Yahoo, Buffalo Rumblings, Russell Street Report)', 'https://sports.yahoo.com/articles/week-8-injury-report-lamar-194753628.html'),
    ('Bengals/Titans (Cincy Jungle)', 'https://www.cincyjungle.com/cincinnati-bengals-injuries/203907/titans-injury-report-carnell-tate-calvin-ridley-tyjae-spears'),
    ('Cardinals/Cowboys (Arizona Sports, SI)', 'https://arizonasports.com/arizona-cardinals-injury-report/cardinals-cowboys-week-8-injury-report-jeremiyah-will-play'),
    ('Vikings/Lions (Pride of Detroit, Vikings.com)', 'https://www.prideofdetroit.com/detroit-lions-injuries/178797/lions-vikings-week-8-injury-designations-kerby-joseph-out-starting-cb-questionable'),
    ('Colts/Jaguars (Big Cat Country, Stampede Blue)', 'https://www.bigcatcountry.com/jacksonville-jaguars-injuries/90594/jaguars-colts-final-injury-report-antonio-johnson-ruled-out'),
    ('Raiders/Jets (Yahoo, NewYorkJets.com)', 'https://sports.yahoo.com/articles/raiders-final-week-8-injury-195753444.html'),
    ('Browns/Steelers (Steelers Depot, Steelers.com)', 'https://steelersdepot.com/2026/10/browns-week-8-friday-injury-report-key-offensive-starter-two-others-questionable/'),
    ('Falcons/Buccaneers (Buccaneers.com, AtlantaFalcons.com)', 'https://www.buccaneers.com/news/buccaneers-falcons-injury-report-oct-30-week-8'),
    ('Chargers/Rams (Chargers.com, TheRams.com)', 'https://www.chargers.com/news/chargers-vs-rams-injury-report-mcconkey-full-james-awosika-don-t-practice-wednesday'),
    ('Chiefs/Broncos (Arrowhead Pride, SI)', 'https://www.arrowheadpride.com/kansas-city-chiefs-injuries/214616/chiefs-broncos-week-8-final-injury-report-rashee-rice-returning'),
    ('Patriots/Dolphins (Pats Pulpit, Patriots.com)', 'https://www.patspulpit.com/new-england-patriots-news/142405/patriots-vs-dolphins-friday-injury-report-a-j-brown-questionable-week-8'),
    ('Eagles/Commanders (Bleeding Green Nation, Commanders.com)', 'https://www.bleedinggreennation.com/philadelphia-eagles-injuries/188756/eagles-commanders-final-injury-report-saquon-barkley-will-play'),
    ('Bears/Seahawks (Seahawks.com, jueves)', 'https://www.seahawks.com/news/week-8-injury-report-bears-at-seahawks'),
    ('Resumen CBS Sports', 'https://www.cbssports.com/nfl/news/nfl-week-8-injury-report-lamar-jackson-aj-brown-emeka-egbuka-more/'),
]
TEAM_NAME = {
    'ARI': 'Arizona Cardinals', 'ATL': 'Atlanta Falcons', 'BAL': 'Baltimore Ravens', 'BUF': 'Buffalo Bills', 'CAR': 'Carolina Panthers',
    'CHI': 'Chicago Bears', 'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns', 'DAL': 'Dallas Cowboys', 'DEN': 'Denver Broncos',
    'DET': 'Detroit Lions', 'GB': 'Green Bay Packers', 'HOU': 'Houston Texans', 'IND': 'Indianapolis Colts', 'JAX': 'Jacksonville Jaguars',
    'KC': 'Kansas City Chiefs', 'LA': 'Los Angeles Rams', 'LAC': 'Los Angeles Chargers', 'LV': 'Las Vegas Raiders', 'MIA': 'Miami Dolphins',
    'MIN': 'Minnesota Vikings', 'NE': 'New England Patriots', 'NO': 'New Orleans Saints', 'NYG': 'New York Giants', 'NYJ': 'New York Jets',
    'PHI': 'Philadelphia Eagles', 'PIT': 'Pittsburgh Steelers', 'SEA': 'Seattle Seahawks', 'SF': 'San Francisco 49ers', 'TB': 'Tampa Bay Buccaneers',
    'TEN': 'Tennessee Titans', 'WAS': 'Washington Commanders',
}
