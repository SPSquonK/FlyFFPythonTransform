This script uses a WorldDialog.txt and a NpcScript.cpp file.

The result is a file like this :

```
/* dudk_drian */ 
// Speak
Bienvenue dans le domaine des Keakoons jeune aventurier. Tu m'as l'air d'être quelqu'un de confiance… pourrais-tu me rendre un service ?
// Say
Hmmm... Comment un être humain comme toi a-t-il pu parvenir jusqu'ici ?!
Merci de secourir mon père. Mais au fait, qu'est ce qui t'amène ici ?
S'il te plaît, sauve mon père. Il est emprisonné à l'est du village des Keakoons.
Hmmm... Je ne sais pas comment tu es arrivé ici, mais tu n'es pas celui dont j'ai besoin. File d'ici, cet endroit est bien trop dangereux pour toi.
Hmmm... Je m'appelle Drian, et je suis le fils de Nevil, le Grand Chef des Keakoons.
Hmmm....  Cet endroit est bien trop dangereux, rentre à la maison ça vaudra mieux pour toi.
Voici les affaires que m'a confiées mon père.
/* dudk_kazen */ 
// Speak
Hmmm… cela risque de prendre un moment...
// Say
Huh… un humain ? Ici ? Tu dois être vraiment brave… ou alors complètement fou !
Quoi ! Un humain… Tu n'es pas le bienvenu sur ces terres. Tu ferais mieux de déguerpir au plus vite.
Hmmm... Je n'ai pas à me présenter à un être humain comme toi.
Rentre chez toi ! Les êtres humains ne sont pas les bienvenus ici.
```

The goal is to have a base file when every normal dialog are compiled. The motivation is to rebuild the dialog system of FlyFF without the quest system which is not ergonomic.

I think FlyFF is not played for its quests, so getting rid of the complicated system behind it, and replacing npc dialogs with a simple system and the "do thing to get items" with another system (like achievement system).