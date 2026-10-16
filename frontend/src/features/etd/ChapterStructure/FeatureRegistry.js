export const loaders = {

    // Chapter 1
    "Ch1:classification": () => import("../Ch1/Classification/ClassificationPresenter"),
    "Ch1:description": () => import("../Ch1/Description/DescriptionPresenter"),
    "Ch1:doc": () => import("../Ch1/Doc/DocPresenter"),
    "Ch1:generation": () => import("../Ch1/Generation/GenerationPresenter"),
    "Ch1:modeOfOperation": () => import("../Ch1/ModeOfOperation/ModeOfOperationPresenter"),
    "Ch1:rawMaterials": () => import("../Ch1/RawMaterials/RawMaterialsPresenter"),
    "Ch1:substances": () => import("../Ch1/Substances/SubstancesPresenter"),
    "Ch1:udi": () => import("../Ch1/Udi/UdiPresenter"),

    // Chapter 2
    "Ch2:ifu": () => import("../Ch2/IfuPresenter"),
    "Ch2:label": () => import("../Ch2/LabelPresenter"),

    // Chapter 3
    "Ch3:descDesign": () => import("../Ch3/DescDesignPresenter"),
    "Ch3:descManu": () => import("../Ch3/DescManuPresenter"),
    "Ch3:descQC": () => import("../Ch3/DescQCPresenter"),
    "Ch3:OutsProc": () => import("../Ch3/OutsProcPresenter"),

    // Chapter 4
    "Ch4:gspr": () => import("../Ch4/GsprPresenter"),

    // Chapter 5
    "Ch5:riskAna": () => import("../Ch5/RiskAnaPresenter"),
    "Ch5:riskPlan": () => import("../Ch5/RiskPlanPresenter"),
    "Ch5:riskRep": () => import("../Ch5/RiskRepPresenter"),

    // Chapter 6
    "Ch6:abcTesting": () => import("../Ch6/AbcTestingPresenter"),
    "Ch6:bioComp": () => import("../Ch6/BioCompPresenter"),
    "Ch6:clinicalEval": () => import("../Ch6/ClinicalEvalPresenter"),
    "Ch6:eSafety": () => import("../Ch6/ESafetyPresenter"),
    "Ch6:safetyPerf": () => import("../Ch6/SafetyPerfPresenter"),
    "Ch6:stability": () => import("../Ch6/StabilityPresenter"),
    "Ch6:SwVV": () => import("../Ch6/SwVVPresenter"),

    // Chapter 2
    "Ch7:pmsPlan": () => import("../Ch7/PmsPlanPresenter"),
    "Ch7:psur": () => import("../Ch7/PsurPresenter"),
}