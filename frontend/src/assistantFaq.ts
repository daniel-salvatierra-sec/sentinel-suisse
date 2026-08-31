import type { Lang } from "./i18n";

/**
 * Canned answers for the most common questions, matched by keyword before ever calling
 * the paid AI backend. Every real support/forum question about apps like this one tends
 * to repeat: is it free, how do alerts work, how do I cancel, is my data safe, etc. —
 * answering those instantly (for free, with zero AI tokens) also means the reply is
 * always accurate and never "hallucinated", and only genuinely open-ended questions
 * reach the LLM. Keep adding stems here over time as real users ask new things.
 *
 * Matching: each entry has one or more "groups" of alternative word stems (fragments,
 * not full sentences, so conjugations like cancel/cancelo/cancelar/cancelación all hit
 * the same stem "cancel"). A message matches an entry only if EVERY group has at least
 * one stem present — e.g. cancel_subscription requires an action stem ("cancel",
 * "resili"...) AND a topic stem ("premium", "abonnement"...), so "cancel my search"
 * alone won't wrongly trigger a subscription answer.
 */

type FaqEntry = {
  id: string;
  match: Record<Lang, string[][]>;
  answer: Record<Lang, string>;
};

function normalize(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const FAQ_ENTRIES: FaqEntry[] = [
  {
    id: "where_is_account",
    match: {
      fr: [
        ["ou est", "ou se trouve", "ou trouver", "ou cliquer"],
        ["compte"],
      ],
      de: [
        ["wo ist", "wo finde", "wo liegt"],
        ["konto"],
      ],
      es: [
        ["donde", "donde esta", "donde queda", "encuent", "hallar"],
        ["cuenta"],
      ],
      pt: [
        ["onde", "onde esta", "onde fica"],
        ["conta"],
      ],
      en: [
        ["where is", "where s", "where can i find", "where do i find"],
        ["account"],
      ],
    },
    answer: {
      fr: "Le bouton Compte est en haut à droite. Je vous y emmène. [[gesture:account]]",
      de: "Der Knopf Konto ist oben rechts. Ich führe Sie dorthin. [[gesture:account]]",
      es: "El botón Cuenta está arriba a la derecha. La llevo ahora. [[gesture:account]]",
      pt: "O botão Conta está no canto superior direito. Levo-o já. [[gesture:account]]",
      en: "The Account button is at the top right. I'll take you there. [[gesture:account]]",
    },
  },
  {
    id: "cancel_subscription",
    match: {
      fr: [
        ["annul", "resili", "arret", "stopp", "desabonn"],
        ["abonnement", "premium", "souscription"],
      ],
      de: [
        ["kundig", "kuendig", "stornier", "abbestell", "beend"],
        ["abo", "abonnement", "premium"],
      ],
      es: [
        ["cancel", "anul", "dar de baja", "desuscri", "desactiv"],
        ["suscripcion", "abono", "premium", "membresia"],
      ],
      pt: [
        ["cancel", "anul", "desinscrev", "desativ"],
        ["assinatura", "subscricao", "premium"],
      ],
      en: [
        ["cancel", "unsubscrib", "stop pay", "end my sub", "terminat"],
        ["subscription", "premium", "plan", "membership"],
      ],
    },
    answer: {
      fr: "Tu peux annuler à tout moment : va dans Compte → « Gérer l'abonnement ». Ça ouvre le portail Stripe où tu peux résilier en un clic, sans nous contacter. Tu gardes Premium jusqu'à la fin de la période déjà payée.",
      de: "Du kannst jederzeit kündigen: Konto → „Abo verwalten“. Das öffnet das Stripe-Kundenportal, wo du in einem Klick kündigen kannst. Premium bleibt bis zum Ende der bezahlten Periode aktiv.",
      es: "Puedes cancelar cuando quieras: ve a Cuenta → «Gestionar suscripción». Eso abre el portal de Stripe, donde cancelas con un clic, sin tener que escribirnos. Sigues teniendo Premium hasta el final del periodo ya pagado.",
      pt: "Podes cancelar quando quiseres: vai a Conta → «Gerir subscrição». Isso abre o portal da Stripe, onde cancelas com um clique, sem precisares de nos contactar. Mantens o Premium até ao fim do período já pago.",
      en: "You can cancel anytime: go to Account → \"Manage subscription\". That opens the Stripe customer portal where you can cancel in one click, no need to contact us. You keep Premium until the end of the period you already paid for.",
    },
  },
  {
    id: "premium_price",
    match: {
      fr: [
        ["combien", "prix", "tarif", "cout"],
        ["premium", "abonnement"],
      ],
      de: [
        ["kostet", "preis", "wie viel", "kosten"],
        ["premium", "abo"],
      ],
      es: [
        ["cuanto cuesta", "cuanto vale", "precio", "tarifa", "cuanto sale"],
        ["premium", "suscripcion"],
      ],
      pt: [
        ["quanto custa", "preco", "quanto e"],
        ["premium", "assinatura"],
      ],
      en: [
        ["how much", "price", "cost"],
        ["premium", "subscription"],
      ],
    },
    answer: {
      fr: "LinkSwiss Premium coûte 9,90 CHF/mois, payable par carte ou TWINT. Ça débloque les alertes automatiques (email + WhatsApp), jusqu'à 5 recherches enregistrées, et les projets neufs à la location. La recherche elle-même reste gratuite pour tout le monde.",
      de: "LinkSwiss Premium kostet 9.90 CHF/Monat, zahlbar per Karte oder TWINT. Damit erhältst du automatische Alerts (E-Mail + WhatsApp), bis zu 5 gespeicherte Suchen und Neuvermietungen / Neubauprojekte. Die Suche selbst bleibt für alle kostenlos.",
      es: "LinkSwiss Premium cuesta 9,90 CHF/mes, con tarjeta o TWINT. Con eso desbloqueas las alertas automáticas (email + WhatsApp), hasta 5 búsquedas guardadas, y proyectos nuevos listos para candidatar. La búsqueda en sí sigue siendo gratis para todos.",
      pt: "O LinkSwiss Premium custa 9,90 CHF/mês, com cartão ou TWINT. Isso desbloqueia os alertas automáticos (email + WhatsApp), até 5 pesquisas guardadas, e projetos novos prontos a candidatar. A pesquisa em si continua gratuita para todos.",
      en: "LinkSwiss Premium costs CHF 9.90/month, payable by card or TWINT. It unlocks automatic alerts (email + WhatsApp), up to 5 saved searches, and new-build projects open for applications. Search itself stays free for everyone.",
    },
  },
  {
    id: "free_search",
    match: {
      fr: [["gratuit", "payant", "faut il payer"]],
      de: [["kostenlos", "gratis", "bezahlen um zu suchen", "kostet es etwas"]],
      es: [["gratis", "gratuito", "pagar para buscar", "cuesta buscar"]],
      pt: [["gratis", "pagar para pesquisar", "custa pesquisar"]],
      en: [["is it free", "free to search", "pay to search", "free or paid", "does it cost"]],
    },
    answer: {
      fr: "Chercher un logement ou un emploi sur LinkSwiss est 100% gratuit, sans compte, sans limite. Tu ne paies que si tu veux qu'on te prévienne automatiquement (email/WhatsApp) dès qu'une nouvelle offre correspond — ça, c'est Premium.",
      de: "Die Wohnungs- und Jobsuche auf LinkSwiss ist 100% kostenlos, ohne Konto, ohne Limit. Bezahlt wird nur, wenn du automatisch benachrichtigt werden willst (E-Mail/WhatsApp), sobald ein neues Angebot passt — das ist Premium.",
      es: "Buscar vivienda o empleo en LinkSwiss es 100% gratis, sin cuenta, sin límite. Solo pagas si quieres que te avisemos automáticamente (email/WhatsApp) en cuanto aparezca una oferta que encaje — eso es Premium.",
      pt: "Pesquisar casa ou emprego no LinkSwiss é 100% grátis, sem conta, sem limite. Só pagas se quiseres que te avisemos automaticamente (email/WhatsApp) assim que aparecer uma oferta que combine — isso é o Premium.",
      en: "Searching for housing or jobs on LinkSwiss is 100% free, no account, no limit. You only pay if you want us to notify you automatically (email/WhatsApp) as soon as a new listing matches — that's Premium.",
    },
  },
  {
    id: "how_alerts_work",
    match: {
      fr: [["alerte"], ["fonctionne", "marche", "c est quoi", "activer", "creer"]],
      de: [["alert", "benachrichtigung"], ["funktionier", "was ist", "aktivier", "erstell"]],
      es: [["alerta"], ["funciona", "que es", "activo", "creo", "llegan"]],
      pt: [["alerta"], ["funciona", "o que e", "ativo", "crio"]],
      en: [["alert", "notification"], ["how do", "what is", "set up", "create"]],
    },
    answer: {
      fr: "Une alerte, c'est une recherche que tu enregistres (ville, type de bien/poste, prix…). Dès qu'une nouvelle offre correspond, on t'envoie un email — et un message WhatsApp aussi si tu es Premium. Sans Premium, la recherche reste enregistrée mais rien n'est envoyé automatiquement.",
      de: "Ein Alert ist eine gespeicherte Suche (Stadt, Wohnungs-/Jobtyp, Preis…). Sobald ein neues Angebot passt, schicken wir dir eine E-Mail — mit Premium zusätzlich eine WhatsApp-Nachricht. Ohne Premium bleibt die Suche gespeichert, aber es wird nichts automatisch verschickt.",
      es: "Una alerta es una búsqueda que guardas (ciudad, tipo de piso/empleo, precio…). En cuanto aparece una oferta que encaja, te mandamos un email — y también un WhatsApp si tienes Premium. Sin Premium, la búsqueda queda guardada pero no se envía nada automáticamente.",
      pt: "Um alerta é uma pesquisa que guardas (cidade, tipo de imóvel/emprego, preço…). Assim que aparece uma oferta que combina, enviamos um email — e também um WhatsApp se tiveres Premium. Sem Premium, a pesquisa fica guardada mas não é enviado nada automaticamente.",
      en: "An alert is a search you save (city, listing/job type, price…). As soon as a new listing matches, we send you an email — plus a WhatsApp message if you're Premium. Without Premium, the search stays saved but nothing is sent automatically.",
    },
  },
  {
    id: "whatsapp_alerts",
    match: {
      fr: [["whatsapp"]],
      de: [["whatsapp"]],
      es: [["whatsapp"]],
      pt: [["whatsapp"]],
      en: [["whatsapp"]],
    },
    answer: {
      fr: "Les alertes WhatsApp sont réservées à Premium. Ajoute ton numéro dans Compte, on t'envoie un message à confirmer (réponds OK), et ensuite tu reçois les nouvelles offres directement sur WhatsApp.",
      de: "WhatsApp-Alerts sind Premium vorbehalten. Trag deine Nummer im Konto ein, wir schicken dir eine Bestätigungsnachricht (antworte mit OK), und danach bekommst du neue Angebote direkt auf WhatsApp.",
      es: "Las alertas por WhatsApp son solo para Premium. Añade tu número en Cuenta, te mandamos un mensaje para confirmar (responde OK), y a partir de ahí recibes las nuevas ofertas directo por WhatsApp.",
      pt: "Os alertas por WhatsApp são só para Premium. Adiciona o teu número em Conta, enviamos-te uma mensagem para confirmar (responde OK), e depois recebes as novas ofertas diretamente no WhatsApp.",
      en: "WhatsApp alerts are Premium-only. Add your number in Account, we'll send you a confirmation message (reply OK), and after that you'll get new listings straight on WhatsApp.",
    },
  },
  {
    id: "lost_login",
    match: {
      fr: [
        ["perdu", "oublie", "impossible de me connecter", "comment me connecter", "plus acces"],
        ["cle", "compte", "connect", "mot de passe", "login"],
      ],
      de: [
        ["verloren", "vergessen", "kann mich nicht anmelden", "wie melde ich mich"],
        ["schlussel", "schluessel", "konto", "anmeld", "passwort", "login"],
      ],
      es: [
        ["perdi", "olvide", "no puedo entrar", "no puedo iniciar", "como inicio"],
        ["clave", "cuenta", "conect", "contrasena", "sesion", "login"],
      ],
      pt: [
        ["perdi", "esqueci", "nao consigo entrar", "como faco login"],
        ["chave", "conta", "liga", "palavra passe", "sessao", "login"],
      ],
      en: [
        ["lost", "forgot", "can t log in", "cant log in", "how do i log in"],
        ["key", "account", "connect", "password", "login"],
      ],
    },
    answer: {
      fr: "Pas de panique, il n'y a pas de mot de passe à retenir. Va dans Compte → « Se connecter », entre ton email, et on t'envoie un lien magique (valable 20 min) qui te reconnecte directement, sans rien à taper.",
      de: "Keine Sorge, es gibt kein Passwort zu merken. Gehe zu Konto → „Anmelden“, gib deine E-Mail ein, und wir schicken dir einen Magic Link (20 Min. gültig), der dich direkt wieder einloggt.",
      es: "Tranquilo, no hay contraseña que recordar. Ve a Cuenta → «Iniciar sesión», pon tu email, y te mandamos un enlace mágico (válido 20 min) que te reconecta directo, sin escribir nada más.",
      pt: "Sem stress, não há palavra-passe para lembrar. Vai a Conta → «Iniciar sessão», põe o teu email, e enviamos-te um link mágico (válido 20 min) que te liga logo de volta, sem escreveres mais nada.",
      en: "No worries, there's no password to remember. Go to Account → \"Log in\", enter your email, and we'll send you a magic link (valid 20 min) that logs you straight back in — nothing else to type.",
    },
  },
  {
    id: "listings_real",
    match: {
      fr: [["reel", "vrai", "faux", "exemple", "demonstration"]],
      de: [["echt", "falsch", "beispiel", "demo"]],
      es: [["real", "falso", "ejemplo", "prueba", "demostracion"]],
      pt: [["real", "falso", "exemplo", "teste", "demonstracao"]],
      en: [["real", "fake", "example listing", "is this a test", "demo"]],
    },
    answer: {
      fr: "Tu peux voir un badge « Exemple » sur certaines cartes : ce sont des annonces de démonstration, pas de vraies offres — le lien externe ne fonctionne pas exprès. Les annonces sans ce badge viennent de vraies sources et le lien vers l'offre originale fonctionne.",
      de: "Manche Karten haben ein „Beispiel“-Label: Das sind Demo-Anzeigen, keine echten Angebote — der externe Link ist absichtlich deaktiviert. Anzeigen ohne dieses Label stammen aus echten Quellen und der Link zum Original funktioniert.",
      es: "Verás una etiqueta «Ejemplo» en algunas tarjetas: son anuncios de demostración, no ofertas reales — el enlace externo está desactivado a propósito. Los anuncios sin esa etiqueta vienen de fuentes reales y el enlace a la oferta original funciona.",
      pt: "Vês uma etiqueta «Exemplo» em alguns cartões: são anúncios de demonstração, não ofertas reais — o link externo está desativado de propósito. Os anúncios sem essa etiqueta vêm de fontes reais e o link para a oferta original funciona.",
      en: "You'll see an \"Example\" badge on some cards: those are demo listings, not real offers — the external link is intentionally disabled. Listings without that badge come from real sources and the link to the original offer works.",
    },
  },
  {
    id: "delete_account",
    match: {
      fr: [["supprim", "effac", "detruire"], ["compte", "donnees", "profil"]],
      de: [["losch", "loesch", "entfern"], ["konto", "daten", "profil"]],
      es: [["borrar", "eliminar", "destruir"], ["cuenta", "datos", "perfil"]],
      pt: [["apagar", "eliminar", "remover"], ["conta", "dados", "perfil"]],
      en: [["delete", "remove", "erase"], ["account", "data", "profile"]],
    },
    answer: {
      fr: "Va dans Compte → « Supprimer mon compte ». Tes données personnelles (email, numéro, historique) sont effacées définitivement, conformément à la LPD/RGPD. Cette action est irréversible.",
      de: "Gehe zu Konto → „Konto löschen“. Deine persönlichen Daten (E-Mail, Nummer, Verlauf) werden gemäss DSG/DSGVO endgültig gelöscht. Diese Aktion kann nicht rückgängig gemacht werden.",
      es: "Ve a Cuenta → «Eliminar mi cuenta». Tus datos personales (email, número, historial) se borran definitivamente, conforme a la LPD/RGPD. Esta acción no se puede deshacer.",
      pt: "Vai a Conta → «Eliminar a minha conta». Os teus dados pessoais (email, número, histórico) são apagados definitivamente, em conformidade com a LPD/RGPD. Esta ação é irreversível.",
      en: "Go to Account → \"Delete my account\". Your personal data (email, phone, history) is permanently erased, in line with Swiss FADP/GDPR. This action can't be undone.",
    },
  },
  {
    id: "listing_source",
    match: {
      fr: [["d ou viennent", "quelle source", "proprietaire", "employeur"], ["annonce", "offre"]],
      de: [["woher", "welche quelle", "vermieter", "arbeitgeber"], ["anzeige", "angebot"]],
      es: [["de donde vienen", "que fuente", "propietario", "empleador"], ["anuncio", "oferta"]],
      pt: [["de onde vem", "que fonte", "proprietario", "empregador"], ["anuncio", "oferta"]],
      en: [["where do", "what source", "landlord", "employer"], ["listing", "ad", "offer"]],
    },
    answer: {
      fr: "LinkSwiss n'est ni propriétaire ni employeur — on rassemble des annonces publiques de portails comme Homegate, Flatfox, ImmoScout24, jobs.ch et d'autres (et bientôt France Travail côté français). Vérifie toujours les détails sur l'annonce originale avant de candidater.",
      de: "LinkSwiss ist weder Vermieter noch Arbeitgeber — wir sammeln öffentliche Anzeigen von Portalen wie Homegate, Flatfox, ImmoScout24, jobs.ch und weiteren. Prüfe die Details immer auf der Original-Anzeige, bevor du dich bewirbst.",
      es: "LinkSwiss no es propietario ni empleador — reunimos anuncios públicos de portales como Homegate, Flatfox, ImmoScout24, jobs.ch y otros (y pronto France Travail del lado francés). Verifica siempre los detalles en el anuncio original antes de aplicar.",
      pt: "O LinkSwiss não é proprietário nem empregador — reunimos anúncios públicos de portais como Homegate, Flatfox, ImmoScout24, jobs.ch e outros. Verifica sempre os detalhes no anúncio original antes de te candidatares.",
      en: "LinkSwiss isn't the landlord or employer — we aggregate public listings from portals like Homegate, Flatfox, ImmoScout24, jobs.ch and others (soon France Travail on the French side). Always check the details on the original listing before applying.",
    },
  },
  {
    id: "saved_search_limit",
    match: {
      fr: [["combien"], ["recherche"]],
      de: [["wie viele"], ["such"]],
      es: [["cuantas", "cuantos"], ["busqueda", "alerta"]],
      pt: [["quantas", "quantos"], ["pesquisa", "alerta"]],
      en: [["how many"], ["search", "alert"]],
    },
    answer: {
      fr: "Sans Premium, tu peux enregistrer 1 recherche. Avec Premium, jusqu'à 5 recherches en même temps, chacune avec sa propre alerte email/WhatsApp.",
      de: "Ohne Premium kannst du 1 Suche speichern. Mit Premium bis zu 5 gleichzeitig, jede mit eigenem E-Mail/WhatsApp-Alert.",
      es: "Sin Premium puedes guardar 1 búsqueda. Con Premium, hasta 5 al mismo tiempo, cada una con su propia alerta de email/WhatsApp.",
      pt: "Sem Premium podes guardar 1 pesquisa. Com Premium, até 5 ao mesmo tempo, cada uma com o seu próprio alerta de email/WhatsApp.",
      en: "Without Premium you can save 1 search. With Premium, up to 5 at the same time, each with its own email/WhatsApp alert.",
    },
  },
  {
    id: "change_language",
    match: {
      fr: [["langue"]],
      de: [["sprache"]],
      es: [["idioma"]],
      pt: [["idioma"]],
      en: [["language"]],
    },
    answer: {
      fr: "En haut de l'écran, il y a un sélecteur FR/DE/ES/PT/EN — clique sur ta langue préférée, tout change instantanément.",
      de: "Oben auf dem Bildschirm gibt es einen FR/DE/ES/PT/EN-Umschalter — klicke auf deine bevorzugte Sprache, alles ändert sich sofort.",
      es: "Arriba de la pantalla hay un selector FR/DE/ES/PT/EN — toca tu idioma preferido y todo cambia al instante.",
      pt: "No topo do ecrã há um seletor FR/DE/ES/PT/EN — toca no teu idioma preferido e tudo muda instantaneamente.",
      en: "At the top of the screen there's an FR/DE/ES/PT/EN switcher — tap your preferred language and everything changes instantly.",
    },
  },
  {
    id: "coverage_area",
    match: {
      fr: [["quelle ville", "quel pays", "quelle region", "ca marche ou"]],
      de: [["welche stadt", "welches land", "welche region", "wo funktioniert"]],
      es: [["que ciudad", "que pais", "que region", "donde funciona"]],
      pt: [["que cidade", "que pais", "onde funciona"]],
      en: [["what cit", "what countr", "which region", "where does this work"]],
    },
    answer: {
      fr: "LinkSwiss couvre la Suisse, la France, l'Allemagne et l'Italie. Dans chaque pays voisin, la première ville est Frontière-Suisse (communes collées à la Suisse), puis les villes de plus de 500 000 habitants. Cherche ta ville pour voir ce qui est déjà en ligne.",
      de: "LinkSwiss deckt die Schweiz, Frankreich, Deutschland und Italien ab. In den Nachbarländern ist die erste Stadt Grenze-Schweiz (Orte an der Schweizer Grenze), danach Städte über 500 000 Einwohner. Suche deine Stadt, um zu sehen, was schon da ist.",
      es: "LinkSwiss cubre Suiza, Francia, Alemania e Italia. En cada país vecino la primera ciudad es Frontera-Suiza (localidades junto a Suiza, no otras fronteras del país) y luego las ciudades de más de 500 000 habitantes. Busca tu ciudad para ver qué hay ya disponible.",
      pt: "O LinkSwiss cobre a Suíça, a França, a Alemanha e a Itália. Em cada país vizinho a primeira cidade é Fronteira-Suíça (localidades junto à Suíça), depois as cidades com mais de 500 000 habitantes. Pesquisa a tua cidade para ver o que já existe.",
      en: "LinkSwiss covers Switzerland, France, Germany and Italy. In each neighbouring country the first city is Swiss border (towns next to Switzerland, not other borders), then cities over 500,000 people. Search your city to see what's already listed.",
    },
  },
  {
    id: "how_to_apply",
    match: {
      fr: [["postul", "candidat", "contacter le proprietaire", "contacter l employeur"]],
      de: [["bewerb", "kontaktiere den vermieter", "kontaktiere den arbeitgeber"]],
      es: [["aplico", "postulo", "postular", "aplicar", "contacto al propietario"]],
      pt: [["candidato", "candidatar", "aplicar", "contacto o proprietario"]],
      en: [["how do i apply", "apply for", "contact the landlord", "contact the employer"]],
    },
    answer: {
      fr: "Ouvre l'annonce, clique sur « Voir l'annonce » (ou « Ça m'intéresse ») — ça t'emmène directement sur le site de l'employeur ou du bailleur d'origine pour candidater ou les contacter. LinkSwiss ne gère pas les candidatures lui-même.",
      de: "Öffne die Anzeige und klicke auf „Anzeige ansehen“ (oder „Interessiert“) — das führt dich direkt zur ursprünglichen Website des Arbeitgebers oder Vermieters, um dich zu bewerben oder Kontakt aufzunehmen. LinkSwiss verwaltet Bewerbungen nicht selbst.",
      es: "Abre el anuncio y toca «Ver anuncio» (o «Me interesa») — te lleva directo al sitio original del empleador o propietario para aplicar o contactarlo. LinkSwiss no gestiona las candidaturas.",
      pt: "Abre o anúncio e toca em «Ver anúncio» (ou «Tenho interesse») — isso leva-te diretamente ao site original do empregador ou proprietário para te candidatares ou contactares. O LinkSwiss não gere as candidaturas.",
      en: "Open the listing and tap \"View listing\" (or \"I'm interested\") — that takes you straight to the original employer's or landlord's site to apply or get in touch. LinkSwiss doesn't handle applications itself.",
    },
  },
  {
    id: "report_bug",
    match: {
      fr: [["bug", "probleme technique", "ne marche pas", "erreur sur le site", "plante"]],
      de: [["fehler", "technisches problem", "funktioniert nicht", "sturzt ab"]],
      es: [["error", "problema tecnico", "no funciona", "falla", "se cierra sola"]],
      pt: [["erro", "problema tecnico", "nao esta a funcionar", "falha"]],
      en: [["bug", "technical problem", "not working", "is broken", "crashes"]],
    },
    answer: {
      fr: "Désolé pour la gêne ! Décris-moi le problème ici (ce que tu faisais, ce qui s'est passé) et je transmets, ou écris directement à l'adresse indiquée en bas de page dans « Mentions légales ».",
      de: "Entschuldige die Unannehmlichkeiten! Beschreib mir das Problem hier (was du gemacht hast, was passiert ist), oder schreib direkt an die Adresse unten im „Impressum“.",
      es: "¡Perdona las molestias! Cuéntame aquí qué estabas haciendo y qué pasó, o escribe directamente a la dirección indicada abajo en «Aviso legal».",
      pt: "Desculpa o incómodo! Conta-me aqui o que estavas a fazer e o que aconteceu, ou escreve diretamente para o endereço indicado em baixo no «Aviso legal».",
      en: "Sorry about that! Tell me here what you were doing and what happened, or write directly to the address listed at the bottom in \"Legal notice\".",
    },
  },
  {
    id: "who_are_you",
    match: {
      fr: [["qui es tu", "c est quoi sentinel", "tu es qui", "tu es un robot", "tu es humain"]],
      de: [["wer bist du", "was ist sentinel", "bist du ein roboter", "bist du ein mensch"]],
      es: [["quien eres", "que es sentinel", "eres un robot", "eres humano", "eres una persona"]],
      pt: [["quem es tu", "o que e o sentinel", "es um robo", "es humano"]],
      en: [["who are you", "what is sentinel", "are you a robot", "are you human"]],
    },
    answer: {
      fr: "Je suis Sentinel, l'assistant de LinkSwiss — un guide automatisé (pas un humain) là pour t'aider à trouver un logement ou un emploi, comprendre les alertes et Premium, et répondre à tes questions sur l'appli.",
      de: "Ich bin Sentinel, der Assistent von LinkSwiss — ein automatisierter Guide (kein Mensch), der dir hilft, eine Wohnung oder einen Job zu finden, Alerts und Premium zu verstehen und deine Fragen zur App zu beantworten.",
      es: "Soy Sentinel, el asistente de LinkSwiss — una guía automatizada (no una persona) para ayudarte a encontrar vivienda o empleo, entender las alertas y Premium, y responder tus preguntas sobre la app.",
      pt: "Sou o Sentinel, o assistente do LinkSwiss — um guia automatizado (não uma pessoa) para te ajudar a encontrar casa ou emprego, entender os alertas e o Premium, e responder às tuas perguntas sobre a app.",
      en: "I'm Sentinel, LinkSwiss's assistant — an automated guide (not a human) here to help you find housing or a job, understand alerts and Premium, and answer your questions about the app.",
    },
  },
  {
    id: "greeting",
    match: {
      fr: [["bonjour", "salut", "coucou", "bonsoir"]],
      de: [["hallo", "guten tag", "servus", "hoi"]],
      es: [["hola", "buenas", "buenos dias", "buenas tardes", "buenas noches"]],
      pt: [["ola", "boa tarde", "bom dia", "boa noite"]],
      en: [["hello", "hi there", "good morning", "good evening"]],
    },
    answer: {
      fr: "Bonjour ! Que puis-je faire pour toi : chercher un logement, un emploi, comprendre les alertes, ou autre chose ?",
      de: "Hallo! Wie kann ich dir helfen: Wohnung suchen, Job finden, Alerts verstehen, oder etwas anderes?",
      es: "¡Hola! ¿En qué te ayudo: buscar vivienda, buscar empleo, entender las alertas, o algo más?",
      pt: "Olá! Em que te posso ajudar: procurar casa, procurar emprego, entender os alertas, ou outra coisa?",
      en: "Hi there! How can I help: finding housing, finding a job, understanding alerts, or something else?",
    },
  },
  {
    id: "thanks",
    match: {
      fr: [["merci"]],
      de: [["danke"]],
      es: [["gracias"]],
      pt: [["obrigad"]],
      en: [["thank"]],
    },
    answer: {
      fr: "Avec plaisir ! Je suis là si tu as d'autres questions. 🙂",
      de: "Gern geschehen! Ich bin da, wenn du weitere Fragen hast. 🙂",
      es: "¡Con gusto! Aquí estoy si tienes más preguntas. 🙂",
      pt: "De nada! Estou aqui se tiveres mais perguntas. 🙂",
      en: "You're welcome! I'm here if you have more questions. 🙂",
    },
  },
];

const SUPPORTED_LANGS: string[] = ["fr", "de", "es", "pt", "en"];

const FOLLOW_UP_STARTS = [
  "y ",
  "e ",
  "et ",
  "und ",
  "and ",
  "ok",
  "vale",
  "bueno",
  "pues",
  "entonces",
  "tambien",
  "si ",
  "yes",
  "oui",
  "ja",
  "eso",
  "esto",
  "cela",
  "isso",
  "that",
];

/** Short replies that only make sense with the previous turn. */
export function isFollowUp(message: string): boolean {
  const normalized = normalize(message);
  const words = normalized.split(" ").filter(Boolean);
  if (words.length === 0) return false;
  if (words.length <= 8 && FOLLOW_UP_STARTS.some((stem) => {
    const exact = stem.trim();
    return normalized === exact || normalized.startsWith(`${exact} `);
  })) {
    return true;
  }
  if (words.length <= 10 && /\b(eso|esto|ello|cela|das|isso|that|it)\b/.test(normalized)) {
    return true;
  }
  return false;
}

/** Returns a canned answer if the message clearly matches a known FAQ, else null. */
export function matchFaq(
  message: string,
  lang: string,
  opts?: { hasHistory?: boolean },
): string | null {
  const normalized = normalize(message);
  if (!normalized) return null;
  if (opts?.hasHistory && isFollowUp(message)) return null;
  const key: Lang = SUPPORTED_LANGS.includes(lang) ? (lang as Lang) : "en";
  for (const entry of FAQ_ENTRIES) {
    if (opts?.hasHistory && (entry.id === "greeting" || entry.id === "thanks")) {
      continue;
    }
    const groups = entry.match[key] ?? entry.match.en;
    const isMatch = groups.every((group) =>
      group.some((stem) => normalized.includes(normalize(stem))),
    );
    if (isMatch) {
      return entry.answer[key] ?? entry.answer.en;
    }
  }
  return null;
}
