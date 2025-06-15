\documentclass{article}

\usepackage[french]{babel}
\usepackage{float}
\usepackage[letterpaper,top=2cm,bottom=2cm,left=3cm,right=3cm,marginparwidth=1.75cm]{geometry}

% Useful packages
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage[colorlinks=true, allcolors=blue]{hyperref}

\title{Modèle 3.2}

\usepackage[T1]{fontenc}
\begin{document}
\maketitle
\date{}
\section{Introduction}


Notre mission était de déterminer la capacité thermique de chaque système, selon un découpage du monde issu d’un travail réalisé l’année dernière (modèle 3 quokka feal). La capacité thermique étant nécessaire dans le code pour la simulation. Dans cette partie, nous allons expliquer notre démarche pour établir les capacités thermiques qui nous seront nécessaires dans la simulation, finalement on distinguera deux valeurs de capcités thermiques : pour l'eau et pour la terre.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.80\linewidth]{Capture d'écran 2025-06-13 141549.png}
    \caption{Planisphère de la Terre découpé par région }
    \label{fig:enter-label}
\end{figure}



\section{1er essai : Capacité thermique selon différentes régions (cf graphique ci-dessus)}

Nous avons cherché la capacité thermique massique des carrés de continent. Pour cela, nous avons étudié la composition du sol dans chaque zone découpée, en identifiant les types de sols présents.

\vspace{1cm}

Ensuite, nous avons relevé la capacité thermique de chaque type de sol afin de calculer une valeur représentative pour la zone concernée.

Nous avons ensuite constaté que la capacité thermique est une grandeur extensive, c’est-à-dire qu’elle dépend du volume du système. C’est pourquoi nous avons choisi d’exprimer la capacité thermique de chaque système en fonction de trois paramètres : la capacité thermique massique, la masse volumique du sol, et le volume considéré (soit la surface multipliée par la profondeur).
\vspace{1cm}

\[ 
C = C_m \cdot \mu \cdot S \cdot d 
\]


\vspace{1cm}
Dans notre cas, la surface de chaque carré ensoleillé est de 1 m², et on a choisi une profondeur de 10 cm venant d'un des exercices du cours des deuxièmes années.

Un premier travail d’estimation avait été réalisé à l’aide de ChatGPT, afin d’obtenir des ordres de grandeur pour chaque zone. Cependant, ce travail, bien qu’utile, devait être complété par une vraie démarche de recherche documentaire avec des sources fiables. Ce que nous avons essayé de faire : nous avons identifié, pour chaque zone, les trois informations clés nécessaires à la formule finale — la composition des sols, leur capacité thermique massique, et leur masse volumique.

\vspace{1cm}

Dans un deuxième temps, nous avons envisagé un découpage de la surface en plusieurs grandes zones : une pour chaque continent, une pour les océans et une pour les zones glaciaires afin de prendre en compte les différences de composition des sols et donc de capacité thermique.

Nous avons d'abord concentré nos recherches sur l'Europe en consultant le \textit{European Soil Data Center}.


\begin{figure}[H]
    \centering
    \includegraphics[width=0.5\linewidth]{carte sols europe.png}
    \caption{Topsoil physical properties for Europe (based on LUCAS topsoil data)}
\end{figure}


La carte présentée ci-dessus montre que les principaux types de sols européens sont : \textit{sandy loam}, \textit{loam}, et \textit{clay loam}. En analysant le document suivant : 
\begin{figure}[H]
    \centering
    \includegraphics[width=0.5\linewidth]{Capture d’écran 2025-06-13 à 16.49.08.png}
\end{figure}
\url{https://www.agrireseau.net/references/6/Bio99-3.pdf}, nous avons obtenu les compositions typiques suivantes :
\begin{itemize}
    \item Loam : 41\,\% de sable, 19\,\% d’argile, et 40\% autres
    \item Sandy loam : 65\,\% de sable, 10\,\% d’argile, et 25\% autres
     \item Clay loam : 31\,\% de sable, 35\,\% d'argile, et 34\% autres.
\end{itemize}


En croisant ces données avec les capacités thermiques massiques des composants, c'est-à-dire argile et sable uniquement (par manque de données) on peut déterminer les capacités thermiques massiques des éléments qui nous intéressent. Après recherche on trouve que la capacité thermique massique du sable est de \(835~\mathrm{J{\cdot}kg^{-1}{\cdot}K^{-1}}\), de meme pour l'argile \(1350~\mathrm{J{\cdot}kg^{-1}{\cdot}K^{-1}}\) .On fait une moyenne en ne prenant en compte que le sable et l'argile des types de sols. On trouve alors une capacité thermique massique d'environ \(1000~\mathrm{J{\cdot}kg^{-1}{\cdot}K^{-1}}\) pour les sols européens. Un travail similaire mené sur l'Afrique a conduit à une valeur proche, de l’ordre de \(1034~\mathrm{J{\cdot}kg^{-1}{\cdot}K^{-1}}\).


Cependant, cette méthode reposant sur des estimations et des données peu précises s'est révélée peu cohérente, en effet on va par la suite préférer faire un modèle plus approximatif avec des données plus sûres qu'un modèle précis avec des données peu fiables.

Nous avons donc décidé de simplifier notre modèle en adoptant une modélisation plus globale, on distingue uniquement la terre et l'eau (distinction terre/ océans). Les différentes valeurs calculées étant toutes proches de \(1000~\mathrm{J{\cdot}kg^{-1}{\cdot}K^{-1}}\), nous avons réorienté nos recherches vers des estimations globales plus fiables.

\section{Capacité thermique finale}

Une source de référence issue du \textit{Materials Handbook} (écrit par un ingénieur chimiste) propose une valeur moyenne de capacité thermique pour les sols terrestres de :
\[
1046~\mathrm{J{\cdot}kg^{-1}{\cdot}K^{-1}}
\]

Cette valeur est également confirmée par d'autres sources indépendantes. Nous avons donc choisi de l’adopter comme valeur de référence pour l’ensemble des parties émergées de la Terre.

Concernant les océans, la capacité thermique de l’eau est bien connue, elle est de : \[
4180~\mathrm{J{\cdot}kg^{-1}{\cdot}K^{-1}}
\]

\section{Code Python}

Dans notre projet, nous avons repris le code d’un des modèles de l’année dernière (le modèle 3 de quokka Feal), qui découpe le monde en zones selon la longitude et la latitude. Ce code permet de déterminer l’albédo de chaque zone.

Notre objectif était de le combiner avec notre propre modèle 3, qui modélise l’évolution de la température de la surface terrestre en fonction de la position géographique (latitude et longitude) et du jour de l’année, à 24 points horaires répartis sur une journée.

Nous souhaitions donc ajouter à ce modèle une bibliothèque de capacités thermiques spécifiques à chaque zone. Cela aurait permis de faire varier la capacité thermique dans la formule utilisée pour calculer l’allure de la température au cours de la journée, et ainsi obtenir une simulation plus réaliste.

Cependant, après avoir constaté qu’il était impossible de trouver des données précises sur la capacité thermique de chaque zone, nous avons finalement choisi de conserver une capacité thermique constante pour l’ensemble des zones, comme mentionné précédemment.

Pour améliorer le modèle on peut utiliser un API (à faire dans les prochains modèles).

\end{document}
