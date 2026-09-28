export const NEEDS = [
 {id:'lines',label:'Suivre les lignes',short:'Les lignes',icon:'lines',text:'Je perds ma ligne ou ma place dans le texte. Propose un essai de repères de lecture et d’espacement, sans imposer une police ou un réglage universel.'},
 {id:'attention',label:'Rester concentré·e',short:'La concentration',icon:'focus',text:'Mon attention décroche pendant la lecture. Propose des points de reprise et une hiérarchie stable ; évite de multiplier les éléments décoratifs ou les sollicitations.'},
 {id:'words',label:'Déchiffrer les mots',short:'Les mots',icon:'words',text:'Déchiffrer les mots me demande un effort. Compare sur un extrait une présentation sobre et lisible à l’original, selon mes préférences. Ne suppose pas qu’une police dite spécialisée me conviendra.'},
 {id:'understand',label:'Comprendre les phrases',short:'Les phrases',icon:'understand',text:'Comprendre les phrases et leurs liens me demande un effort. Rends les relations existantes plus faciles à suivre en respectant mon choix sur la reformulation. Ne crée pas d’explication, d’exemple ou de connaissance absente de la synthèse.'},
 {id:'locate',label:'Retrouver une information',short:'Le repérage',icon:'locate',text:'J’ai du mal à retrouver une information. Propose une hiérarchie de titres existants et des repères de navigation cohérents, sans modifier l’ordre logique sans mon accord.'},
 {id:'overload',label:'Éviter la surcharge',short:'Moins de surcharge',icon:'overload',text:'La densité ou la quantité de repères me surcharge. Limite les effets ajoutés et montre une variante sobre. Conserve les repères qui ont déjà un sens pour moi.'},
 {id:'numbers',label:'Lire chiffres et tableaux',short:'Chiffres et tableaux',icon:'numbers',text:'Les chiffres, formules ou tableaux me demandent un effort. Conserve exactement nombres, signes, unités et relations entre cellules. Vérifie alignement, coupures et lisibilité ; aucune simplification de calcul ni de valeur.'},
 {id:'memory',label:'Garder le fil des idées',short:'Le fil des idées',icon:'memory',text:'Garder le fil des idées me demande un effort. Propose des repères stables et des regroupements fidèles au contenu. N’ajoute ni résumé, ni moyen mnémotechnique, ni contenu pédagogique.'},
 {id:'fatigue',label:'Limiter la fatigue',short:'La fatigue',icon:'fatigue',text:'Je me fatigue pendant la lecture. Demande quel effort pèse le plus si je ne l’ai pas précisé. Commence par un essai court et pose une seule question à la fois.'},
 {id:'navigation',label:'Naviguer dans le document',short:'La navigation',icon:'navigation',text:'Naviguer dans le document me demande un effort. Vérifie la structure, les titres, les liens et l’ordre de lecture avec mon moyen d’accès. Ne remplace pas une vraie structure par des effets visuels.'}
];
const WORDING = {
 intact:'Conserve mes mots exacts. Modifie uniquement la présentation et la structure d’accès ; aucune reformulation, suppression ou ajout au texte. Les descriptions alternatives de visuels doivent être fidèles au visuel observé et confirmées si leur sens est incertain.',
 rephrase:'Tu peux proposer une reformulation sur un petit extrait, à côté de l’original, avant tout traitement complet. Préserve chaque information, terme technique, nuance, exception, citation et lien logique. Signale les modifications et attends mon retour ; ne résume pas.'
};
const COLORS = {
 preserve:'Préserve les couleurs existantes et leur sens. N’ajoute pas de codage couleur sans me proposer un essai.',
 none:'N’ajoute aucune couleur. Préserve les couleurs existantes porteuses de sens. Si une version monochrome est nécessaire, propose d’abord des repères équivalents explicites et attends mon accord.',
 try:'Propose un essai avec quelques repères colorés, sans modifier les couleurs existantes porteuses de sens. Ne véhicule aucune information par la seule couleur ; vérifie le contraste sur le fond réel.'
};
const SPACING = {
 ask:'L’espacement reste à essayer ensemble : ne change pas mes réglages par défaut. Propose une comparaison limitée sur un extrait.',
 preserve:'Conserve la disposition, les espacements et les dimensions actuels. Si un besoin semble nécessiter une modification de disposition, explique le conflit et demande mon choix avant de modifier.',
 airy:'Propose un essai plus aéré sur un extrait, avec des espacements ajustables. Vérifie les coupures de mots, la pagination et les tableaux : davantage d’espace ne doit pas faire perdre les repères.'
};
const SUPPORT = {
 unknown:'Mon support n’est pas encore défini. Clarifie-le si cela change les adaptations proposées.',
 screen:'Je lirai sur écran. Vérifie le rendu au zoom et sur la taille d’écran utilisée, sans imposer un fond ou une palette.',
 paper:'Je lirai sur papier. Vérifie la taille réelle imprimée, les marges, les sauts de page et le rendu en niveaux de gris si nécessaire.',
 both:'Je lirai sur écran et sur papier. Distingue les réglages utiles à chaque contexte ; ne suppose pas qu’une version unique convient aux deux.'
};
const ACCESS = {
 visual:'Pour la lecture visuelle, vérifier la lisibilité et le contraste réel des textes, bordures et repères.',
 voice:'Pour la lecture vocale, conserver une restitution intégrale et un ordre compréhensible. Ne pas transformer la synthèse en résumé audio ; annoncer si la génération audio n’est pas disponible.',
 reader:'Pour le lecteur d’écran, vérifier les titres structurés, l’ordre de lecture, les liens explicites, les listes natives, les en-têtes de tableaux et les alternatives fidèles aux images. Ne pas annoncer cette vérification comme faite sans test réel.',
 keyboard:'Pour le clavier, prévoir une navigation logique et des repères accessibles sans souris dans le format choisi.',
 zoom:'Pour le texte agrandi, vérifier les débordements, les coupures et les relations entre cellules. Une taille de caractères seule ne garantit pas une lecture adaptée.'
};
export const DEFAULTS = Object.freeze({needs:[],wording:'intact',color:'preserve',spacing:'ask',support:'unknown',access:[],priority:'',preserve:'',detail:''});
export function assemble(input = {}) {
 const state={...DEFAULTS,...input};
 for(const [key,options] of [['wording',WORDING],['color',COLORS],['spacing',SPACING],['support',SUPPORT]]) if(!Object.hasOwn(options,state[key])) throw new TypeError(`Choix invalide : ${key}`);
 for(const [key,allowed] of [['needs',NEEDS.map(n=>n.id)],['access',Object.keys(ACCESS)]]) if(!Array.isArray(state[key])||state[key].some(v=>!allowed.includes(v))) throw new TypeError(`Choix invalide : ${key}`);
 for(const [key,max] of [['priority',250],['preserve',500],['detail',2000]]) if(typeof state[key]!=='string'||state[key].length>max) throw new TypeError(`Texte invalide : ${key}`);
 const selected=NEEDS.filter(n=>state.needs.includes(n.id));
 const blocks=[`MA DEMANDE\nJe joins une synthèse existante. Aide-moi à la rendre plus accessible pour moi, à partir des besoins et préférences ci-dessous. Ne crée pas de synthèse, ne résume pas un cours et ne traite pas un cours comme une synthèse. Si le fichier manque, demande-le ; si sa nature est ambiguë, clarifie-la avant de le modifier.\n\nConserve toutes les informations, les termes techniques, les nuances, les exceptions, les citations, les nombres, les formules, les tableaux, les images, les liens et les notes. N’invente aucun contenu pédagogique. Préserve mon original.`];
 blocks.push(`MES BESOINS\n${selected.length?selected.map(n=>'- '+n.text).join('\n'):'Je n’ai pas encore précisé mes difficultés. Demande-moi ce qui me gêne, sans déduire un trouble ni imposer un réglage.'}`);
 blocks.push(`MES PRÉFÉRENCES ET LIMITES\n- ${WORDING[state.wording]}\n- ${COLORS[state.color]}\n- ${SPACING[state.spacing]}`);
 blocks.push(`MON CONTEXTE\n${SUPPORT[state.support]}\n${Object.entries(ACCESS).filter(([id])=>state.access.includes(id)).map(([,text])=>'- '+text).join('\n')||'Mon moyen d’accès reste à préciser si nécessaire.'}`);
 const conflicts=[];
 if(selected.some(n=>n.id==='overload')&&state.color==='try') conflicts.push('Surcharge + couleurs : commencer avec très peu de repères et comparer à une version sans ajout.');
 if(selected.some(n=>n.id==='understand')&&state.wording==='intact') conflicts.push('Compréhension + mots exacts : garder le texte intact et tester seulement des repères de structure ; demander mon accord si cela ne suffit pas.');
 if(state.spacing==='preserve'&&selected.some(n=>['lines','words','overload','numbers'].includes(n.id))) conflicts.push('Disposition conservée : ne pas appliquer un nouvel espacement pour répondre à ces besoins sans un choix explicite de ma part.');
 if(state.access.includes('reader')&&state.color==='try') conflicts.push('Lecteur d’écran + couleurs : les repères doivent aussi être disponibles dans la structure et le texte, jamais uniquement dans la couleur.');
 if(conflicts.length) blocks.push('POINTS À ARBITRER AVEC MOI\n'+conflicts.map(c=>'- '+c).join('\n'));
 const free=[];
 if(state.priority.trim()) free.push('Ma priorité (mes mots) :\n'+state.priority);
 if(state.preserve.trim()) free.push('Mes repères à préserver (mes mots) :\n'+state.preserve);
 if(state.detail.trim()) free.push('Mes précisions (mes mots) :\n'+state.detail);
 if(free.length) blocks.push('MES PRÉCISIONS PERSONNELLES\n'+free.join('\n\n'));
 blocks.push(`COMMENT PROCÉDER\n1. Tiens compte de mes besoins ensemble. Mes préférences explicites priment sur tes hypothèses. En cas de contradiction, y compris dans mes précisions libres, explique-la et demande-moi de choisir ; ne tranche pas silencieusement. N’infère aucun réglage depuis un diagnostic.\n2. Choisis avec moi un court extrait représentatif, avec les éléments qui me posent problème. Propose un essai comparé à l’original, adapté à mon moyen d’accès. Ne considère pas cet essai comme une préférence déjà validée.\n3. Demande ce qui aide, gêne ou doit rester inchangé. Accepte que je refuse toutes les variantes. N’applique au document complet que les choix que j’ai confirmés.\n4. Vérifie qu’aucune information n’a disparu et que les transformations n’ont pas changé le sens. Contrôle le rendu et la structure. Si tes outils ne permettent pas de produire ou vérifier un format, dis-le clairement ; ne prétends pas avoir créé ou testé un fichier.\n5. Fournis la synthèse adaptée complète, l’original préservé, un bref bilan des choix et les limites restant à vérifier. Ne présente pas un extrait comme le livrable final, ni le résultat comme « accessible à tous ».`);
 const preferenceTags=[state.wording==='intact'?'Mots exacts':'Reformulation à essayer', {preserve:'Couleurs préservées',none:'Sans ajout de couleurs',try:'Couleurs à essayer'}[state.color], {ask:'Espacement à essayer',preserve:'Disposition conservée',airy:'Plus d’espace à essayer'}[state.spacing]];
 const contextTags=[...(state.support==='unknown'?[]:[{screen:'Écran',paper:'Papier',both:'Écran et papier'}[state.support]]),...Object.keys(ACCESS).filter(k=>state.access.includes(k)).map(k=>({visual:'Lecture visuelle',voice:'Lecture vocale',reader:'Lecteur d’écran',keyboard:'Clavier',zoom:'Zoom'}[k]))];
 return {text:blocks.join('\n\n'),tags:['Le socle commun',...selected.map(n=>n.short),...preferenceTags,...contextTags,...(free.length?['Vos précisions']:[])],conflicts};
}
