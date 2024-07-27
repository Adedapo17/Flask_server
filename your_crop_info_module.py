crop_database = {
    "rice": {
        "growth_stages": {
            "Germination": (100),
            "Seedling": (101, 200),
            "Vegetative Growth": (200, 600),
            "Panicle Initiation": (600, 900),
            "Booting": (900, 1100),
            "Heading": (1100, 1300),
            "Flowering": (1300, 1500),
            "Grain Filling": (1500, 1900),
            "Maturity/Harvest": (1900, 2200)
        },
        "pests_info": [
            {
                "pest": "Rice Stem Borer (Scirpophaga incertulas)",
                "GDD_stage": (200, 1900),
                "symptoms": "Deadheart and whiteheads.",
                "control_options": ["Use resistant varieties", "Apply pheromone traps", "Use biological control agents like Trichogramma spp."]
            },
            {
                "pest": "Rice Leaf Folder (Cnaphalocrocis medinalis)",
                "GDD_stage": (0, 2200),
                "symptoms": "Folded leaves and skeletonized leaves.",
                "control_options": ["Introduce natural predators like spiders and wasps", "Use neem-based products", "Use insecticidal sprays"]
            },
            {
                "pest": "Brown Planthopper (Nilaparvata lugens)",
                "GDD_stage": (200, 2200),
                "symptoms": "Hopperburn and stunted growth.",
                "control_options": ["Implement resistant rice varieties", "Utilize biopesticides", "Use natural predators like mirid bugs"]
            }
        ],
        "agricultural_practices": {
            "Germination": ["Use high-quality, certified seeds", "Maintain optimal soil moisture for uniform germination", "Implement seed priming techniques for better germination"],
            "Seedling": ["Transplant seedlings at the 2-3 leaf stage for optimal growth", "Ensure proper spacing to avoid competition", "Use fertilizers rich in nitrogen to support early growth"],
            "Vegetative Growth": ["Apply appropriate fertilizers based on soil test recommendations", "Perform regular weeding to reduce competition", "Maintain adequate water levels to promote tillering"],
            "Panicle Initiation": ["Apply potassium and phosphorus fertilizers to support panicle development", "Monitor for early signs of pest and disease infestation"],
            "Booting": ["Maintain optimal water levels", "Apply micronutrients if deficiencies are observed"],
            "Heading": ["Ensure water management to avoid stress", "Monitor for pests like stem borers"],
            "Flowering": ["Avoid water stress", "Protect against fungal diseases"],
            "Grain Filling": ["Continue proper irrigation", "Apply appropriate pest management strategies"],
            "Maturity/Harvest": ["Reduce water before harvest to ease threshing", "Harvest at the right moisture content to avoid grain loss"]
        }
    },
    "tomato": {
        "growth_stages": {
            "Germination": (150),
            "Seedling Stage": (151, 300),
            "Vegetative Growth": (300, 700),
            "Flowering": (700, 1000),
            "Fruit Set": (1000, 1200),
            "Fruit Growth": (1200, 1600),
            "Maturity/Harvest": (1600, 1900)
        },
        "pests_info": [
            { 
                "pest": "Cutworms (Agrotis spp.)",
                "GDD_stage": (300, 500),
                "symptoms": "Cut plants at the base.",
                "control_options": ["Use physical barriers like collars around stems.", "Apply biological pesticides such as Bacillus thuringiensis (Bt)."]
            },
            {
                "pest": "Aphids (Aphididae)",
                "GDD_stage": (700, 1200),
                "symptoms": "Yellowing, curled leaves, sticky honeydew.",
                "control_options": ["Introduce beneficial insects like ladybugs and lacewings.", "Use insecticidal soaps or neem oil."]
            },
            {
                "pest": "Tomato Fruitworm (Helicoverpa zea)", 
                "GDD_stage": (1200, 1900),
                "symptoms": "Holes in fruits, internal feeding.",
                "control_options": ["Handpick and destroy worms.", "Use pheromone traps and biological pesticides such as Bt."]
            },
            {
                "pest": "Whiteflies (Bemisia tabaci)",
                "GDD_stage": (0, 1900),
                "symptoms": "Yellowing leaves, honeydew, and sooty mold.",
                "control_options": ["Implement reflective mulches to repel whiteflies.", "Use insecticidal soaps, neem oil, or introduce natural predators like Encarsia formosa."]
            },
            {
                "pest": "Spider Mites (Tetranychus spp.)",
                "GDD_stage": (0, 1900),
                "symptoms": "Speckled leaves, webbing, leaf drop.",
                "control_options": ["Increase humidity around plants.", "Use miticides or insecticidal soaps."]
            },
            {
                "pest": "Tomato Hornworm (Manduca quinquemaculata)",
                "GDD_stage": (300, 1200),
                "symptoms": "Large holes in leaves, defoliation.",
                "control_options": ["Handpick and destroy larvae.", "Introduce natural predators like braconid wasps."]
            }
        ],
        "agricultural_practices": {
            "Germination": ["Ensure consistent soil moisture.", "Maintain optimal temperature for germination."],
            "Seedling Stage": ["Thin out seedlings to avoid overcrowding.", "Provide sufficient light."],
            "Vegetative Growth": ["Ensure proper nutrient supply.", "Implement staking to support plant growth."],
            "Flowering": ["Maintain consistent watering.", "Monitor for pests and diseases."],
            "Fruit Set": ["Continue consistent watering.", "Support branches with heavy fruit load."],
            "Fruit Growth": ["Ensure adequate water and nutrients.", "Monitor for pests and diseases."],
            "Maturity/Harvest": ["Reduce watering to prevent fruit splitting.", "Harvest fruits at optimal ripeness."]
        }
    },
    "maize": {
        "growth_stages": {
            "Germination": (120),
            "Seedling Stage": (121, 475),
            "Vegetative Growth": (475, 950),
            "Tasseling": (950, 1200),
            "Silking": (1200, 1600),
            "Grain Filling": (1600, 2400),
            "Maturity/Harvest": (2400, 2500)
        },
        "pests_info": [
            {
                "pest": "Fall Armyworm (Spodoptera frugiperda)",
                "GDD_stage": (0, 2700),
                "symptoms": "Leaf holes, feeding on kernels.",
                "control_options": ["Use pheromone traps and biological pesticides like Bt.", "Encourage natural predators like parasitic wasps."]
            },
            {
                "pest": "Maize Stalk Borer (Busseola fusca)",
                "GDD_stage": (250, 1200),
                "symptoms": "Boreholes in stems, stunted growth.",
                "control_options": ["Apply insecticides to the base of the plant.", "Use resistant varieties and crop rotation."]
            },
            {
                "pest": "Corn Earworm (Helicoverpa zea)",
                "GDD_stage": (700, 2700),
                "symptoms": "Damage to ears, feeding on kernels.",
                "control_options": ["Handpick and destroy larvae.", "Use pheromone traps and biological pesticides like Bt."]
            }
        ],
        "agricultural_practices": {
            "Germination": ["Use certified, disease-free seeds.", "Maintain adequate soil moisture.", "Ensure proper seed depth and spacing."],
            "Seedling Stage": ["Apply starter fertilizers rich in nitrogen.", "Control weeds to reduce competition.", "Monitor for early pest infestations."],
            "Vegetative Growth": ["Continue fertilization based on soil tests.", "Implement integrated pest management (IPM) strategies.", "Ensure adequate irrigation."],
            "Tasseling": ["Apply potassium and phosphorus fertilizers.", "Monitor for pests and diseases.", "Maintain optimal soil moisture."],
            "Silking": ["Ensure good pollination conditions.", "Protect against pests like corn earworms."],
            "Grain Filling": ["Continue irrigation to support kernel development.", "Apply late-season nitrogen if necessary.", "Protect against fungal infections."],
            "Maturity/Harvest": ["Reduce water before harvest.", "Harvest at the correct moisture content to avoid losses.", "Store properly to avoid post-harvest pests."]
        }
    },
    "beans": {
        "growth_stages": {
            "Germination": (100),
            "Seedling Stage": (101, 200),
            "Vegetative Growth": (200, 400),
            "Flowering": (400, 600),
            "Pod Formation": (600, 800),
            "Pod Filling": (800, 1000),
            "Maturity/Harvest": (1000, 1300)
        },
        "pests_info": [
            {
                "pest": "Bean Aphid (Aphis fabae)",
                "GDD_stage": (400, 1000),
                "symptoms": "Yellowing, curled leaves, sticky honeydew.",
                "control_options": ["Introduce beneficial insects like ladybugs.", "Use insecticidal soaps or neem oil."]
            },
            {
                "pest": "Bean Leaf Beetle (Cerotoma trifurcata)",
                "GDD_stage": (200, 800),
                "symptoms": "Holes in leaves, defoliation.",
                "control_options": ["Handpick beetles.", "Apply neem-based products or insecticides."]
            },
            {
                "pest": "Mexican Bean Beetle (Epilachna varivestis)",
                "GDD_stage": (0, 1200),
                "symptoms": "Skeletonized leaves.",
                "control_options": ["Introduce natural predators like parasitic wasps.", "Use insecticidal soaps or neem oil."]
            }
        ],
        "agricultural_practices": {
            "Germination": ["Use certified seeds.", "Maintain adequate soil moisture.", "Ensure proper seed depth."],
            "Seedling Stage": ["Apply starter fertilizers.", "Control weeds.", "Monitor for early pest infestations."],
            "Vegetative Growth": ["Continue fertilization based on soil tests.", "Implement IPM strategies.", "Ensure adequate irrigation."],
            "Flowering": ["Apply potassium and phosphorus fertilizers.", "Protect against pests.", "Maintain optimal soil moisture."],
            "Pod Formation": ["Continue irrigation.", "Monitor for pests and diseases.", "Apply fertilizers if needed."],
            "Pod Filling": ["Maintain irrigation.", "Protect against fungal infections.", "Ensure good air circulation."],
            "Maturity/Harvest": ["Reduce water before harvest.", "Harvest at the correct moisture content.", "Store properly to avoid post-harvest pests."]
        }
    },
    "millet": {
        "growth_stages": {
            "Germination": (80),
            "Seedling Stage": (81, 160),
            "Vegetative Growth": (160, 400),
            "Panicle Initiation": (400, 600),
            "Flowering": (600, 900),
            "Grain Filling": (900, 1400),
            "Maturity/Harvest": (1400, 1900)
        },
        "pests_info": [
            {
                "pest": "Millet Stem Borer (Coniesta ignefusalis)",
                "GDD_stage": (160, 1000),
                "symptoms": "Deadheart, whiteheads.",
                "control_options": ["Use resistant varieties.", "Apply pheromone traps and biological control agents like Trichogramma spp."]
            },
            {
                "pest": "Greenbug (Schizaphis graminum)",
                "GDD_stage": (0, 1900),
                "symptoms": "Yellowing, stunted growth.",
                "control_options": ["Introduce natural predators like ladybugs.", "Use insecticidal soaps or neem oil."]
            },
            {
                "pest": "Armyworm (Spodoptera spp.)",
                "GDD_stage": (0, 1900),
                "symptoms": "Defoliation, feeding on grains.",
                "control_options": ["Use pheromone traps and biological pesticides like Bt.", "Encourage natural predators like parasitic wasps."]
            }
        ],
        "agricultural_practices": {
            "Germination": ["Use high-quality seeds.", "Maintain soil moisture.", "Ensure proper seed depth and spacing."],
            "Seedling Stage": ["Apply starter fertilizers.", "Control weeds.", "Monitor for early pests."],
            "Vegetative Growth": ["Continue fertilization.", "Implement IPM strategies.", "Ensure adequate irrigation."],
            "Panicle Initiation": ["Apply potassium and phosphorus fertilizers.", "Protect against pests.", "Maintain soil moisture."],
            "Flowering": ["Ensure good pollination conditions.", "Monitor for pests and diseases.", "Maintain adequate irrigation."],
            "Grain Filling": ["Continue irrigation.", "Apply fertilizers if needed.", "Protect against fungal infections."],
            "Maturity/Harvest": ["Reduce water before harvest.", "Harvest at the right moisture content.", "Store properly to avoid post-harvest pests."]
        }
    }
}
