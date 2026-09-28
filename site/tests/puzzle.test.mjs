import {test} from 'node:test';
import assert from 'node:assert/strict';
import {assemble,NEEDS} from '../dist/puzzle.js';

test('sans réponse, demander les besoins sans inventer un profil',()=>{const {text}=assemble();assert.match(text,/Je n’ai pas encore précisé/);assert.match(text,/Conserve mes mots exacts/);assert.match(text,/Ne crée pas de synthèse/);});
test('combinaisons indépendantes de l’ordre et sans doublons',()=>{assert.deepEqual(assemble({needs:['fatigue','lines','lines']}),assemble({needs:['lines','fatigue']}));assert.equal(assemble({needs:['lines']}).text.split('Je perds ma ligne').length,2);});
test('retrait d’une pièce retire sa consigne',()=>{assert.match(assemble({needs:['fatigue']}).text,/Je me fatigue/);assert.doesNotMatch(assemble({needs:[]}).text,/Je me fatigue/);});
test('refus de couleurs, conservation de disposition et texte intact respectés',()=>{const {text,conflicts}=assemble({needs:['understand','lines'],color:'none',spacing:'preserve'});assert.match(text,/N’ajoute aucune couleur/);assert.match(text,/Conserve la disposition/);assert.doesNotMatch(text,/Tu peux proposer une reformulation/);assert.equal(conflicts.length,2);});
test('les combinaisons potentiellement gênantes sont explicites',()=>{const {conflicts}=assemble({needs:['overload'],color:'try',access:['reader']});assert.equal(conflicts.length,2);});
test('accès combinés et papier sans promesse de génération audio',()=>{const {text}=assemble({support:'both',access:['reader','voice','keyboard']});assert.match(text,/écran et sur papier/);assert.match(text,/annoncer si la génération audio n’est pas disponible/);assert.match(text,/sans test réel/);});
test('texte libre préservé à l’identique, sans interprétation ni HTML',()=>{const detail='  Mes mots : <script>alert(1)</script>\nSans changement.  ';assert.ok(assemble({detail}).text.includes(detail));});
test('entrées invalides rejetées avant assemblage',()=>{for(const input of [{needs:['inconnu']},{needs:null},{color:'inventée'},{access:['invalid']},{priority:'a'.repeat(251)},{detail:42}]) assert.throws(()=>assemble(input),TypeError);});
test('toutes les combinaisons de besoins gardent la conservation et la calibration',()=>{for(let mask=0;mask<2**NEEDS.length;mask++){const needs=NEEDS.filter((_,i)=>mask&(1<<i)).map(n=>n.id);const {text}=assemble({needs});assert.match(text,/Conserve toutes les informations/);assert.match(text,/court extrait représentatif/);assert.match(text,/N’applique au document complet que les choix que j’ai confirmés/);}});
