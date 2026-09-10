"""
recommendations.py
------------------
Comprehensive clinical disease descriptions and actionable agronomic remedies
for all 55 PlantVillage & crop disease categories.
"""

DISEASE_INFO = {
    # Apple
    "Apple___Apple_scab": {
        "description": "Fungal infection (Venturia inaequalis) causing olive-green to dark velvety lesions on leaves and fruit, causing distortion and premature defoliation.",
        "treatment": "Rake and destroy fallen leaves to reduce overwintering spores. Apply preventative fungicides (captan, sulfur, or myclobutanil) starting at bud break. Prune trees for open canopy airflow."
    },
    "Apple___Black_rot": {
        "description": "Fungal disease (Botryosphaeria obtusa) causing 'frog-eye' leaf spots with purple margins, sunken cankers on limbs, and firm mummified fruit rot.",
        "treatment": "Prune out all dead wood, cankers, and mummified fruit during dormancy. Disinfect pruning shears between cuts. Apply captan or copper fungicides from silver tip stage."
    },
    "Apple___Cedar_apple_rust": {
        "description": "Fungal pathogen (Gymnosporangium juniperi-virginianae) requiring both junipers and apples to complete its life cycle. Produces bright orange-yellow spots on upper leaf surfaces.",
        "treatment": "Remove nearby eastern red cedar or juniper trees within 1-2 miles if possible. Apply myclobutanil or mancozeb preventative fungicides when orange galls gelatinize on cedars in spring."
    },
    "Apple___healthy": {
        "description": "Foliage and tree tissue appear vigorous with normal chlorophyll pigmentation and structural integrity.",
        "treatment": "Continue regular seasonal pruning, balanced fertilization (N-P-K), and integrated pest monitoring."
    },

    # Blueberry
    "Blueberry___healthy": {
        "description": "Healthy blueberry foliage with uniform green coloration and active shoot development.",
        "treatment": "Maintain acidic soil pH (4.5–5.2), provide organic pine-bark mulch, and sustain consistent irrigation."
    },

    # Cherry
    "Cherry_(including_sour)___Powdery_mildew": {
        "description": "Fungal disease (Podosphaera clandestina) coating leaves and young shoots in white powdery mycelium, leading to leaf curling and stunted terminal growth.",
        "treatment": "Apply sulfur or potassium bicarbonate sprays early in the growing season. Improve air circulation by thinning inner canopy branches. Avoid overhead irrigation."
    },
    "Cherry_(including_sour)___healthy": {
        "description": "Vigorous cherry foliage free of leaf spot or powdery mildew symptoms.",
        "treatment": "Maintain routine fruit tree nutrition, monitor for cherry fruit fly and aphids, and maintain proper soil drainage."
    },

    # Corn
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "description": "Fungal disease (Cercospora zeae-maydis) producing rectangular, tan-to-gray lesions running parallel between leaf veins, causing extensive photosynthesizing tissue loss.",
        "treatment": "Rotate crops with non-grasses (such as soybeans). Choose GLS-tolerant hybrid seeds. Apply strobilurin or triazole fungicides at VT-R1 growth stage if risk is high."
    },
    "Corn_(maize)___Common_rust_": {
        "description": "Fungal pathogen (Puccinia sorghi) causing cinnamon-brown to reddish-orange pustules scattered over both upper and lower leaf surfaces.",
        "treatment": "Plant resistant hybrid varieties. Fungicide application (triazoles/strobilurins) is rarely needed unless infection appears prior to tasseling and weather remains cool and humid."
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "description": "Fungal infection (Exserohilum turcicum) producing large, cigar-shaped grayish-green to tan lesions (1 to 6 inches long) that can merge and scorch entire leaves.",
        "treatment": "Tillage to bury infected corn residue. Rotate crops for at least one year away from corn. Apply labeled foliar fungicides if lesions appear early on upper leaves."
    },
    "Corn_(maize)___healthy": {
        "description": "Healthy maize stalk and foliage displaying deep green color with optimal leaf area index.",
        "treatment": "Maintain side-dress nitrogen applications based on soil testing and ensure adequate water during tasseling and grain fill."
    },

    # Grape
    "Grape___Black_rot": {
        "description": "Destructive fungal disease (Guignardia bidwellii) forming small, circular reddish-brown leaf spots with black fruiting pycnidia, and shriveling grapes into hard black mummies.",
        "treatment": "Sanitation is vital: remove all mummified berries from vines and ground. Prune vines for maximum sun penetration. Apply myclobutanil or mancozeb from early shoot growth through veraison."
    },
    "Grape___Esca_(Black_Measles)": {
        "description": "Complex fungal wood disease causing characteristic 'tiger-stripe' interveinal chlorosis and necrosis on leaves, and purple spots on berries.",
        "treatment": "Avoid making large pruning wounds in wet weather. Paint fresh pruning cuts with wound sealants or Trichoderma formulations. Remove and burn dead vine trunks."
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "description": "Fungal spot disease causing irregular reddish-brown necrotic spots with dark margins on leaves, leading to premature leaf drop late in the season.",
        "treatment": "Ensure canopy management to reduce humidity. Copper oxychloride or mancozeb applications applied after fruit set manage the blight."
    },
    "Grape___healthy": {
        "description": "Normal grape vine canopy with healthy cluster development and leaf vigor.",
        "treatment": "Practice trellis shoot positioning, cluster thinning if necessary, and preventative powdery/downy mildew spray schedules."
    },

    # Orange / Citrus
    "Orange___Citrus_Canker": {
        "description": "Bacterial disease (Xanthomonas citri) causing raised, corky, crater-like lesions surrounded by an oily yellow halo on leaves, twigs, and fruit.",
        "treatment": "Quarantine affected trees. Apply copper-based bactericides at 21-day intervals during flushes of new growth. Install windbreaks to reduce windblown rain dispersal."
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "description": "Severe, incurrable bacterial disease (Candidatus Liberibacter asiaticus) spread by the Asian citrus psyllid, causing asymmetrical blotchy yellowing on leaves, twig dieback, and bitter misshapen fruit.",
        "treatment": "Strict psyllid vector control using systemic insecticides (imidacloprid) or organic horticultural oils. Remove confirmed positive trees immediately to safeguard adjacent groves."
    },
    "Orange___Multiple_Diseases": {
        "description": "Co-infection symptoms presenting combinations of fungal melanose, greasy spot, and nutritional chlorosis.",
        "treatment": "Implement comprehensive orchard sanitation, prune out dead wood, and apply broad-spectrum copper sprays combined with micronutrient foliar feeds (Zinc/Manganese)."
    },
    "Orange___Nutrient_Deficiency": {
        "description": "Interveinal yellowing or mottled leaves typically indicating Zinc, Iron, or Manganese micronutrient shortages or soil pH imbalance.",
        "treatment": "Perform soil and leaf tissue testing. Apply balanced foliar micronutrient sprays (chelated iron, zinc sulfate) and adjust soil pH toward 6.0–6.5."
    },
    "Orange___healthy": {
        "description": "Dark green, glossy citrus foliage with robust branch elongation and clean rind development.",
        "treatment": "Maintain balanced citrus fertilizer schedule (NPK + Mg + Fe), monitor irrigation depth, and inspect for scale and whiteflies."
    },

    # Peach
    "Peach___Bacterial_spot": {
        "description": "Bacterial pathogen (Xanthomonas arboricola pv. pruni) creating small water-soaked spots that turn dark and fall out, giving leaves a 'shot-hole' appearance.",
        "treatment": "Select resistant peach cultivars. Avoid excessive nitrogen which induces tender susceptible growth. Apply preventative copper sprays during dormancy and oxytetracycline during the season."
    },
    "Peach___healthy": {
        "description": "Healthy peach tree foliage displaying uniform spear-shaped green leaves.",
        "treatment": "Maintain open-center pruning for sunlight distribution, monitor for peach tree borer, and spray preventative dormant copper for peach leaf curl."
    },

    # Pepper
    "Pepper,_bell___Bacterial_spot": {
        "description": "Bacterial disease (Xanthomonas campestris pv. vesicatoria) creating dark, greasy water-soaked spots on foliage and raised scabby lesions on peppers.",
        "treatment": "Avoid overhead watering; use drip lines. Apply fixed copper bactericides mixed with mancozeb for synergy. Discard infected plant residue and rotate away from solanaceous crops."
    },
    "Pepper,_bell___healthy": {
        "description": "Vibrant bell pepper foliage with strong blossom set and firm green leaves.",
        "treatment": "Ensure steady moisture to prevent blossom end rot, provide calcium supplementation, and stake plants to support heavy fruit loads."
    },

    # Potato
    "Potato___Early_blight": {
        "description": "Fungal pathogen (Alternaria solani) producing dark brown spots with distinctive concentric rings ('target pattern') on older lower leaves.",
        "treatment": "Prune out infected lower leaves. Avoid overhead irrigation and leaf wetness. Apply fungicides containing chlorothalonil, azoxystrobin, or copper."
    },
    "Potato___Late_blight": {
        "description": "Aggressive, devastating water mold (Phytophthora infestans) causing large dark water-soaked blotches that rot foliage and stems within days under cool, humid conditions.",
        "treatment": "Act immediately: cull and destroy infected foliage. Spray systemic fungicides (cymoxanil, dimethomorph, or copper). Destroy volunteer potatoes and hill soil well over tubers."
    },
    "Potato___healthy": {
        "description": "Sturdy, bushy potato canopy with rich chlorophyll and steady tuber bulking.",
        "treatment": "Maintain hill soil coverage around tuber zones, monitor for Colorado potato beetle, and regulate irrigation."
    },

    # Raspberry
    "Raspberry___healthy": {
        "description": "Healthy raspberry canes with clean serrated trifoliate leaves and active cane growth.",
        "treatment": "Prune out spent floricanes after harvest, thin primocanes to improve aeration, and maintain acidic, well-draining soil."
    },

    # Soybean
    "Soybean___Bacterial_Pustule": {
        "description": "Bacterial pathogen (Xanthomonas axonopodis pv. glycines) causing tiny pale green spots with elevated pustules in the center, turning into reddish-brown ragged tears.",
        "treatment": "Plant resistant soybean cultivars. Bury crop residues with clean tillage. Avoid cultivating fields when foliage is wet from rain or dew."
    },
    "Soybean___Brown_Spot": {
        "description": "Fungal disease (Septoria glycines) causing small, dark brown angular lesions on primary leaves that yellow and drop prematurely.",
        "treatment": "Rotate crops with corn for 1-2 years. Plant high-quality certified seed. Foliar fungicides at R3 stage can be considered if wet weather persists."
    },
    "Soybean___Crestamento": {
        "description": "Cercospora leaf blight causing purplish-bronze discoloration on the upper surface of sun-exposed soybean leaves, with leathery texture.",
        "treatment": "Use pathogen-free seeds, rotate fields, and apply strobilurin or triazole fungicides during pod development (R3–R5)."
    },
    "Soybean___Ferrugen": {
        "description": "Asian soybean rust (Phakopsora pachyrhizi), highly aggressive fungal disease creating tiny tan to dark brown volcanic pustules on lower leaf undersides.",
        "treatment": "Early detection is critical. Apply preventative fungicides (triazoles/strobilurins) at the earliest sign of disease presence in the region."
    },
    "Soybean___Frogeye_Leaf_Spot": {
        "description": "Fungal disease (Cercospora sojina) forming circular to angular gray spots with reddish-purple margins across upper foliage.",
        "treatment": "Utilize frogeye-resistant soybean varieties. Rotate crops with non-host plants. Spray fungicides with dual modes of action to prevent strobilurin resistance."
    },
    "Soybean___Mosaic_Virus": {
        "description": "Viral disease (SMV) transmitted by aphids, causing distinct dark green blistering, puckering, and downward curling along leaf veins.",
        "treatment": "Plant certified virus-free seed. Manage aphid populations early. Infected plants cannot be cured and should be rogued out in seed production."
    },
    "Soybean___Powdery_Mildew": {
        "description": "Fungal coating (Microsphaera diffusa) of white powdery patches spreading across the upper leaf surfaces, reducing light absorption.",
        "treatment": "Most commercial cultivars carry strong genetic resistance. If susceptible varieties are infected early, apply labeled sulfur or azoxystrobin sprays."
    },
    "Soybean___Rust": {
        "description": "Rust spore pustules on soybean foliage causing chlorosis, rapid defoliation, and aborted pod filling.",
        "treatment": "Monitor regional rust spore tracking traps. Apply fungicide cocktails (e.g., prothioconazole + trifloxystrobin) at R1–R3 growth stages."
    },
    "Soybean___Septoria": {
        "description": "Septoria brown spot leading to yellowing and premature dropping of lower canopy leaves following prolonged rain.",
        "treatment": "Ensure crop rotation, improve field drainage, and apply protective fungicide if lesions ascend into the upper canopy."
    },
    "Soybean___Southern_Blight": {
        "description": "Soil-borne fungal pathogen (Sclerotium rolfsii) forming white fan-like mycelium and mustard-seed-sized brown sclerotia around the stem base and lower leaves.",
        "treatment": "Deep plowing to bury sclerotia. Rotate crops with non-susceptible grasses (corn, sorghum). Ensure high organic matter and aeration in the root zone."
    },
    "Soybean___Sudden_Death_Syndrome": {
        "description": "Soil-borne fungus (Fusarium virguliforme) interacting with soybean cyst nematode to produce prominent interveinal chlorosis and necrosis while veins remain green.",
        "treatment": "Plant SDS-tolerant varieties. Treat seeds with fluopyram (ILEVO) or similar targeted nematicide/fungicide seed treatments. Improve soil drainage and reduce compaction."
    },
    "Soybean___Target_Leaf_Spot": {
        "description": "Fungal pathogen (Corynespora cassiicola) causing reddish-brown circular spots with concentric rings, often surrounded by a dull yellow halo.",
        "treatment": "Rotate crops, till residues, and utilize tolerant cultivars. Apply SDHI or triazole fungicides if weather continues humid and warm."
    },
    "Soybean___Yellow_Mosaic": {
        "description": "Geminivirus transmitted by whiteflies (Bemisia tabaci) creating striking alternating yellow and green mosaic patches on leaves.",
        "treatment": "Vector control: spray neem oil, insecticidal soap, or systemic insecticides for whiteflies. Remove weeds hosting the virus near field borders."
    },
    "Soybean___healthy": {
        "description": "Thriving soybean canopy with optimal trifoliate leaf spread and healthy nodulation at the root level.",
        "treatment": "Maintain soil fertility (check Potassium levels), monitor soil moisture during pod fill, and scout for stink bugs and loopers."
    },

    # Squash
    "Squash___Powdery_mildew": {
        "description": "Fungal infection (Podosphaera xanthii) coating broad cucurbit leaves with powder-like white colonies, leading to yellowing, crisping, and sunburned squash.",
        "treatment": "Spray preventative bio-fungicides (Bacillus subtilis, potassium bicarbonate, or neem oil). Space squash hills 4-6 feet apart for sunlight and airflow."
    },

    # Strawberry
    "Strawberry___Leaf_scorch": {
        "description": "Fungal pathogen (Diplocarpon earlianum) producing numerous small, purplish spots that enlarge and merge until the leaf turns brown and curled, appearing scorched.",
        "treatment": "Remove and compost old scorched leaves after renovation. Avoid sprinkler watering; utilize drip tape beneath mulch. Apply captan or copper fungicide."
    },
    "Strawberry___healthy": {
        "description": "Lush green strawberry crowns with clean trifoliate leaves and healthy runner production.",
        "treatment": "Keep fruit off bare soil with straw mulch or plastic, maintain consistent watering during fruit expansion, and manage spider mites."
    },

    # Tomato
    "Tomato___Bacterial_spot": {
        "description": "Bacterial disease causing small, dark, water-soaked greasy spots on leaves and stems, thriving in hot, humid rains.",
        "treatment": "Avoid working with wet plants. Apply copper bactericides combined with mancozeb. Prune out lower infected leaves and sanitize tools."
    },
    "Tomato___Early_blight": {
        "description": "Fungal disease (Alternaria linariae) causing dark concentric ring spots on older leaves, yellowing surrounding tissue and defoliating the vine from bottom upward.",
        "treatment": "Prune lower suckers and leaves touching soil. Apply organic copper or chlorothalonil fungicide. Mulch heavily around bases to halt soil splash."
    },
    "Tomato___Late_blight": {
        "description": "Aggressive, high-risk pathogen (Phytophthora infestans) creating large water-soaked greasy lesions that rapidly rot leaves, stems, and green fruit.",
        "treatment": "Urgent eradication needed: prune and bag infected plants. Apply preventative copper or systemic fungicides (chlorothalonil, mancozeb) and ensure complete canopy aeration."
    },
    "Tomato___Leaf_Mold": {
        "description": "Fungal disease (Passalora fulva) causing pale green to yellow spots on upper leaf surfaces with velvety olive-brown mold underneath, common in humid hoop houses.",
        "treatment": "Increase greenhouse ventilation and lower relative humidity below 85%. Ensure warm airflow and apply labeled bio-fungicides."
    },
    "Tomato___Septoria_leaf_spot": {
        "description": "Fungal disease causing hundreds of tiny circular spots with dark brown margins and pale gray centers, peppered with microscopic black speck pycnidia.",
        "treatment": "Remove infected lower leaves. Water only at the base using drip irrigation. Apply copper fungicides weekly during rainy weather."
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "description": "Arachnid pests that puncture plant cells, leaving speckled yellow flecks, bronzed leaves, and delicate silk webbing across shoots.",
        "treatment": "Hose down leaf undersides with strong water spray. Apply insecticidal soap, neem oil, or sulfur (avoid sulfur above 32°C). Release predatory mites (Phytoseiulus persimilis)."
    },
    "Tomato___Target_Spot": {
        "description": "Fungal pathogen (Corynespora cassiicola) creating brown circular spots with distinct concentric rings, easily mistaken for early blight.",
        "treatment": "Improve crop spacing, prune indeterminate tomatoes to encourage vertical airflow, and apply protective fungicides (chlorothalonil or azoxystrobin)."
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "description": "Devastating viral disease spread by whiteflies, causing stunted bushy growth, severe upward leaf cupping, and complete blossom drop.",
        "treatment": "No chemical cure exists for infected plants. Remove and destroy infected vines. Control whiteflies with yellow sticky traps and horticultural oils. Plant TYLCV-resistant varieties."
    },
    "Tomato___Tomato_mosaic_virus": {
        "description": "Highly contagious tobamovirus causing mottled light and dark green patterns, deformed 'shoestring' leaves, and internal brown fruit browning.",
        "treatment": "Discard infected plants immediately. Sterilize shears in 10% bleach solution. Wash hands thoroughly (especially if using tobacco products) before handling crops."
    },
    "Tomato___healthy": {
        "description": "Robust tomato foliage with rich chlorophyll, sturdy indeterminate stems, and active flower cluster development.",
        "treatment": "Stake or cage plants, maintain consistent watering to avoid blossom end rot, and prune ground-level suckers."
    }
}


def get_recommendations(label: str):
    """
    Returns (clean_title, description, treatment, is_healthy) for a given class label.
    """
    is_healthy = "healthy" in label.lower()
    clean_title = label.replace("___", " — ").replace("__", " ").replace("_", " ")

    if label in DISEASE_INFO:
        info = DISEASE_INFO[label]
        return {
            "title": clean_title,
            "description": info["description"],
            "treatment": info["treatment"],
            "is_healthy": is_healthy
        }

    # Fallback to key matching
    for key, info in DISEASE_INFO.items():
        if key.lower() in label.lower():
            return {
                "title": clean_title,
                "description": info["description"],
                "treatment": info["treatment"],
                "is_healthy": is_healthy
            }

    # Generic fallback
    if is_healthy:
        return {
            "title": clean_title,
            "description": "Foliage shows normal healthy characteristics without active lesions.",
            "treatment": "Maintain balanced moisture, seasonal nutrition, and routine crop scouting.",
            "is_healthy": True
        }
    else:
        return {
            "title": clean_title,
            "description": f"Symptoms indicative of {clean_title} pathogen activity.",
            "treatment": "Isolate affected crops, prune infected leaves, avoid wetting foliage, and consult an agronomist for targeted fungicide or bactericide recommendations.",
            "is_healthy": False
        }
