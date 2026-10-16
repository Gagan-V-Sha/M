import sys
import os
from sqlalchemy.orm import Session
from pathlib import Path

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.core.database import SessionLocal
from app.core import models

MDR_GSPR_DATA = [
    # CHAPTER I: GENERAL REQUIREMENTS
    {
        "full_reference": "GSPR 1",
        "chapter": "Chapter I",
        "section": "General Requirements",
        "text": "Devices shall achieve the performance intended by their manufacturer and shall be designed and manufactured in such a way that, during normal conditions of use, they are suitable for their intended purpose. They shall be safe and effective and shall not compromise the clinical condition or the safety of patients, or the safety and health of users or, where applicable, other persons, provided that any risks which may be associated with their use constitute acceptable risks when weighed against the benefits to the patient and are compatible with a high level of protection of health and safety, taking into account the generally acknowledged state of the art."
    },
    {
        "full_reference": "GSPR 2",
        "chapter": "Chapter I",
        "section": "General Requirements",
        "text": "The requirement in this Annex to reduce risks as far as possible means the reduction of risks as far as possible without adversely affecting the benefit-risk ratio."
    },
    {
        "full_reference": "GSPR 3",
        "chapter": "Chapter I",
        "section": "General Requirements",
        "text": "Manufacturers shall establish, implement, document and maintain a risk management system. Risk management shall be understood as a continuous iterative process throughout the entire lifecycle of a device, requiring regular systematic updating. In carrying out risk management manufacturers shall:",
        "children": [
            {"full_reference": "GSPR 3(a)", "chapter": "Chapter I", "section": "General Requirements", "text": "establish and document a risk management plan for each device;"},
            {"full_reference": "GSPR 3(b)", "chapter": "Chapter I", "section": "General Requirements", "text": "identify and analyse the known and foreseeable hazards associated with each device;"},
            {"full_reference": "GSPR 3(c)", "chapter": "Chapter I", "section": "General Requirements", "text": "estimate and evaluate the risks associated with, and occurring during, the intended use and during reasonably foreseeable misuse;"},
            {"full_reference": "GSPR 3(d)", "chapter": "Chapter I", "section": "General Requirements", "text": "eliminate or control the risks referred to in point (c) in accordance with the requirements of Section 4;"},
            {"full_reference": "GSPR 3(e)", "chapter": "Chapter I", "section": "General Requirements", "text": "evaluate the impact of information from the production phase and, in particular, from the post-market surveillance system, on hazards and the frequency of occurrence thereof, on estimates of their associated risks, as well as on the overall risk, benefit-risk ratio and risk acceptability; and"},
            {"full_reference": "GSPR 3(f)", "chapter": "Chapter I", "section": "General Requirements", "text": "based on the evaluation of the impact of the information referred to in point (e), if necessary amend control measures in line with the requirements of Section 4."}
        ]
    },
    {
        "full_reference": "GSPR 4",
        "chapter": "Chapter I",
        "section": "General Requirements",
        "text": "Risk control measures adopted by manufacturers for the design and manufacture of the devices shall conform to safety principles, taking account of the generally acknowledged state of the art. To reduce risks, Manufacturers shall manage risks so that the residual risk associated with each hazard as well as the overall residual risk is judged acceptable. In selecting the most appropriate solutions, manufacturers shall, in the following order of priority:",
        "children": [
            {"full_reference": "GSPR 4(a)", "chapter": "Chapter I", "section": "General Requirements", "text": "eliminate or reduce risks as far as possible through safe design and manufacture;"},
            {"full_reference": "GSPR 4(b)", "chapter": "Chapter I", "section": "General Requirements", "text": "where appropriate, take adequate protection measures, including alarms if necessary, in relation to risks that cannot be eliminated; and"},
            {"full_reference": "GSPR 4(c)", "chapter": "Chapter I", "section": "General Requirements", "text": "provide information for safety (warnings/precautions/contra-indications) and, where appropriate, training to users."}
        ]
    },
    {
        "full_reference": "GSPR 5",
        "chapter": "Chapter I",
        "section": "General Requirements",
        "text": "In eliminating or reducing risks related to use error, the manufacturer shall:",
        "children": [
            {"full_reference": "GSPR 5(a)", "chapter": "Chapter I", "section": "General Requirements", "text": "reduce as far as possible the risks related to the ergonomic features of the device and the environment in which the device is intended to be used (design for patient safety), and"},
            {"full_reference": "GSPR 5(b)", "chapter": "Chapter I", "section": "General Requirements", "text": "give consideration to the technical knowledge, experience, education, training and use environment, where applicable, and the medical and physical conditions of intended users (design for lay, professional, disabled or other users)."}
        ]
    },
    {
        "full_reference": "GSPR 6",
        "chapter": "Chapter I",
        "section": "General Requirements",
        "text": "The characteristics and performance of a device shall not be adversely affected to such a degree that the health or safety of the patient or the user and, where applicable, of other persons are compromised during the lifetime of the device, as indicated by the manufacturer, when the device is subjected to the stresses which can occur during normal conditions of use and has been properly maintained in accordance with the manufacturer's instructions."
    },
    {
        "full_reference": "GSPR 7",
        "chapter": "Chapter I",
        "section": "General Requirements",
        "text": "Devices shall be designed, manufactured and packaged in such a way that their characteristics and performance during their intended use are not adversely affected during transport and storage, for example, through fluctuations of temperature and humidity, taking account of the instructions and information provided by the manufacturer."
    },
    {
        "full_reference": "GSPR 8",
        "chapter": "Chapter I",
        "section": "General Requirements",
        "text": "All known and foreseeable risks, and any undesirable side-effects, shall be minimised and be acceptable when weighed against the evaluated benefits to the patient and/or user arising from the achieved performance of the device during normal conditions of use."
    },
    {
        "full_reference": "GSPR 9",
        "chapter": "Chapter I",
        "section": "General Requirements",
        "text": "For the devices referred to in Annex XVI, the general safety requirements set out in Sections 1 and 8 shall be understood to mean that the device, when used under the conditions and for the purposes intended, does not present a risk at all or presents a risk that is no more than the maximum acceptable risk related to the product's use which is consistent with a high level of protection for the safety and health of persons."
    },
    # CHAPTER II: REQUIREMENTS REGARDING DESIGN AND MANUFACTURE
    {
        "full_reference": "GSPR 10.1",
        "chapter": "Chapter II",
        "section": "Chemical, physical and biological properties",
        "text": "Devices shall be designed and manufactured in such a way as to ensure that the characteristics and performance requirements referred to in Chapter I are fulfilled. Particular attention shall be paid to:",
        "children": [
            {"full_reference": "GSPR 10.1(a)", "chapter": "Chapter II", "section": "Chemical, physical and biological properties", "text": "the choice of materials and substances used, particularly as regards toxicity and, where relevant, flammability;"},
            {"full_reference": "GSPR 10.1(b)", "chapter": "Chapter II", "section": "Chemical, physical and biological properties", "text": "the compatibility between the materials and substances used and biological tissues, cells and body fluids, taking account of the intended purpose of the device and, where relevant, absorption, distribution, metabolism and excretion;"},
            {"full_reference": "GSPR 10.1(c)", "chapter": "Chapter II", "section": "Chemical, physical and biological properties", "text": "the compatibility between the different parts of a device which consists of more than one implantable part;"},
            {"full_reference": "GSPR 10.1(d)", "chapter": "Chapter II", "section": "Chemical, physical and biological properties", "text": "the impact of processes on material properties;"},
            {"full_reference": "GSPR 10.1(e)", "chapter": "Chapter II", "section": "Chemical, physical and biological properties", "text": "where appropriate, the results of biophysical or modelling research the validity of which has been demonstrated beforehand;"},
            {"full_reference": "GSPR 10.1(f)", "chapter": "Chapter II", "section": "Chemical, physical and biological properties", "text": "the mechanical properties of the materials used, reflecting, where appropriate, matters such as strength, ductility, fracture resistance, wear resistance and fatigue resistance;"},
            {"full_reference": "GSPR 10.1(g)", "chapter": "Chapter II", "section": "Chemical, physical and biological properties", "text": "surface properties; and"},
            {"full_reference": "GSPR 10.1(h)", "chapter": "Chapter II", "section": "Chemical, physical and biological properties", "text": "the confirmation that the device meets any defined chemical and/or physical specifications."}
        ]
    },
    {
        "full_reference": "GSPR 10.2",
        "chapter": "Chapter II",
        "section": "Chemical, physical and biological properties",
        "text": "Devices shall be designed, manufactured and packaged in such a way as to minimise the risk posed by contaminants and residues to patients, taking account of the intended purpose of the device, and to the persons involved in the transport, storage and use of the devices. Particular attention shall be paid to tissues exposed to those contaminants and residues and to the duration and frequency of exposure."
    },
    {
        "full_reference": "GSPR 10.3",
        "chapter": "Chapter II",
        "section": "Chemical, physical and biological properties",
        "text": "Devices shall be designed and manufactured in such a way that they can be used safely with the materials and substances, including gases, with which they enter into contact during their intended use; if the devices are intended to administer medicinal products they shall be designed and manufactured in such a way as to be compatible with the medicinal products concerned in accordance with the provisions and restrictions governing those medicinal products and that the performance of both the medicinal products and of the devices is maintained in accordance with their respective indications and intended use."
    },
    {
        "full_reference": "GSPR 10.4.1",
        "chapter": "Chapter II",
        "section": "Substances",
        "text": "Devices shall be designed and manufactured in such a way as to reduce as far as possible the risks posed by substances or particles, including wear debris, degradation products and processing residues, that may be released from the device. Devices, or those parts thereof or those materials used therein that: — are invasive and come into direct contact with the human body, — (re)administer medicines, body liquids or other substances, including gases, to/from the body, or — transport or store such medicines, body fluids or substances, including gases, to be (re)administered to the body, shall only contain the following substances in a concentration that is above 0,1 % weight by weight (w/w) where justified pursuant to Section 10.4.2:",
        "children": [
            {"full_reference": "GSPR 10.4.1(a)", "chapter": "Chapter II", "section": "Substances", "text": "substances which are carcinogenic, mutagenic or toxic to reproduction (‘CMR’), of category 1A or 1B, in accordance with Part 3 of Annex VI to Regulation (EC) No 1272/2008 of the European Parliament and of the Council, or"},
            {"full_reference": "GSPR 10.4.1(b)", "chapter": "Chapter II", "section": "Substances", "text": "substances having endocrine-disrupting properties for which there is scientific evidence of probable serious effects to human health and which are identified either in accordance with the procedure set out in Article 59 of Regulation (EC) No 1907/2006 of the European Parliament and of the Council or, once a delegated act has been adopted by the Commission pursuant to the first subparagraph of Article 5(3) of Regulation (EU) No 528/2012 of the European Parliament and the Council, in accordance with the criteria that are relevant to human health amongst the criteria established therein."}
        ]
    },
    {
        "full_reference": "GSPR 10.4.2",
        "chapter": "Chapter II",
        "section": "Substances",
        "text": "The justification for the presence of such substances shall be based upon:",
        "children": [
            {"full_reference": "GSPR 10.4.2(a)", "chapter": "Chapter II", "section": "Substances", "text": "an analysis and estimation of potential patient or user exposure to the substance;"},
            {"full_reference": "GSPR 10.4.2(b)", "chapter": "Chapter II", "section": "Substances", "text": "an analysis of possible alternative substances, materials or designs, including, where available, information about independent research, peer-reviewed studies, scientific opinions from relevant scientific committees and an analysis of the availability of such alternatives;"},
            {"full_reference": "GSPR 10.4.2(c)", "chapter": "Chapter II", "section": "Substances", "text": "argumentation as to why possible substance and/ or material substitutes, if available, or design changes, if feasible, are inappropriate in relation to maintaining the functionality, performance and the benefit-risk ratios of the product; including taking into account if the intended use of such devices includes treatment of children or treatment of pregnant or breastfeeding women or treatment of other patient groups considered particularly vulnerable to such substances and/or materials; and"},
            {"full_reference": "GSPR 10.4.2(d)", "chapter": "Chapter II", "section": "Substances", "text": "where applicable and available, the latest relevant scientific committee guidelines in accordance with Sections 10.4.3. and 10.4.4."}
        ]
    },
    {
        "full_reference": "GSPR 10.4.3",
        "chapter": "Chapter II",
        "section": "Substances",
        "text": "For the purposes of Section 10.4., the Commission shall, as soon as possible and by 26 May 2018, provide the relevant scientific committee with a mandate to prepare guidelines that shall be ready before 26 May 2020. The mandate for the committee shall encompass at least a benefit-risk assessment of the presence of phthalates which belong to either of the groups of substances referred to in points (a) and (b) of Section 10.4.1. The benefit-risk assessment shall take into account the intended purpose and context of the use of the device, as well as any available alternative substances and alternative materials, designs or medical treatments. When deemed appropriate on the basis of the latest scientific evidence, but at least every five years, the guidelines shall be updated."
    },
    {
        "full_reference": "GSPR 10.4.4",
        "chapter": "Chapter II",
        "section": "Substances",
        "text": "Subsequently, the Commission shall mandate the relevant scientific committee to prepare guidelines as referred to in Section 10.4.3. also for other substances referred to in points (a) and (b) of Section 10.4.1., where appropriate."
    },
    {
        "full_reference": "GSPR 10.4.5",
        "chapter": "Chapter II",
        "section": "Substances",
        "text": "Where devices, parts thereof or materials used therein as referred to in Section 10.4.1. contain substances referred to in points (a) or (b) of Section 10.4.1. in a concentration above 0,1 % weight by weight (w/w), the presence of those substances shall be labelled on the device itself and/or on the packaging for each unit or, where appropriate, on the sales packaging, with the list of such substances. If the intended use of such devices includes treatment of children or treatment of pregnant or breastfeeding women or treatment of other patient groups considered particularly vulnerable to such substances and/or materials, information on residual risks for those patient groups and, if applicable, on appropriate precautionary measures shall be given in the instructions for use."
    },
    {
        "full_reference": "GSPR 10.5",
        "chapter": "Chapter II",
        "section": "Chemical, physical and biological properties",
        "text": "Devices shall be designed and manufactured in such a way as to reduce as far as possible the risks posed by the unintentional ingress of substances into the device taking into account the device and the nature of the environment in which it is intended to be used."
    },
    {
        "full_reference": "GSPR 10.6",
        "chapter": "Chapter II",
        "section": "Chemical, physical and biological properties",
        "text": "Devices shall be designed and manufactured in such a way as to reduce as far as possible the risks linked to the size and the properties of particles which are or can be released into the patient's or user's body, unless they come into contact with intact skin only. Special attention shall be given to nanomaterials."
    },
    {
        "full_reference": "GSPR 11.1",
        "chapter": "Chapter II",
        "section": "Infection and microbial contamination",
        "text": "Devices and their manufacturing processes shall be designed in such a way as to eliminate or to reduce as far as possible the risk of infection to patients, users and, where applicable, other persons. The design shall:",
        "children": [
            {"full_reference": "GSPR 11.1(a)", "chapter": "Chapter II", "section": "Infection and microbial contamination", "text": "reduce as far as possible and appropriate the risks from unintended cuts and pricks, such as needle stick injuries,"},
            {"full_reference": "GSPR 11.1(b)", "chapter": "Chapter II", "section": "Infection and microbial contamination", "text": "allow easy and safe handling,"},
            {"full_reference": "GSPR 11.1(c)", "chapter": "Chapter II", "section": "Infection and microbial contamination", "text": "reduce as far as possible any microbial leakage from the device and/or microbial exposure during use, and"},
            {"full_reference": "GSPR 11.1(d)", "chapter": "Chapter II", "section": "Infection and microbial contamination", "text": "prevent microbial contamination of the device or its content such as specimens or fluids."}
        ]
    },
    {
        "full_reference": "GSPR 11.2",
        "chapter": "Chapter II",
        "section": "Infection and microbial contamination",
        "text": "Where necessary devices shall be designed to facilitate their safe cleaning, disinfection, and/or re-sterilisation."
    },
    {
        "full_reference": "GSPR 11.3",
        "chapter": "Chapter II",
        "section": "Infection and microbial contamination",
        "text": "Devices labelled as having a specific microbial state shall be designed, manufactured and packaged to ensure that they remain in that state when placed on the market and remain so under the transport and storage conditions specified by the manufacturer."
    },
    {
        "full_reference": "GSPR 11.4",
        "chapter": "Chapter II",
        "section": "Infection and microbial contamination",
        "text": "Devices delivered in a sterile state shall be designed, manufactured and packaged in accordance with appropriate procedures, to ensure that they are sterile when placed on the market and that, unless the packaging which is intended to maintain their sterile condition is damaged, they remain sterile, under the transport and storage conditions specified by the manufacturer, until that packaging is opened at the point of use. It shall be ensured that the integrity of that packaging is clearly evident to the final user."
    },
    {
        "full_reference": "GSPR 11.5",
        "chapter": "Chapter II",
        "section": "Infection and microbial contamination",
        "text": "Devices labelled as sterile shall be processed, manufactured, packaged and, sterilised by means of appropriate, validated methods."
    },
    {
        "full_reference": "GSPR 11.6",
        "chapter": "Chapter II",
        "section": "Infection and microbial contamination",
        "text": "Devices intended to be sterilised shall be manufactured and packaged in appropriate and controlled conditions and facilities."
    },
    {
        "full_reference": "GSPR 11.7",
        "chapter": "Chapter II",
        "section": "Infection and microbial contamination",
        "text": "Packaging systems for non-sterile devices shall maintain the integrity and cleanliness of the product and, where the devices are to be sterilised prior to use, minimise the risk of microbial contamination; the packaging system shall be suitable taking account of the method of sterilisation indicated by the manufacturer."
    },
    {
        "full_reference": "GSPR 11.8",
        "chapter": "Chapter II",
        "section": "Infection and microbial contamination",
        "text": "The labelling of the device shall distinguish between identical or similar devices placed on the market in both a sterile and a non-sterile condition additional to the symbol used to indicate that devices are sterile."
    },
    {
        "full_reference": "GSPR 12.1",
        "chapter": "Chapter II",
        "section": "Medicinal products and substances absorbed",
        "text": "In the case of devices referred to in the first subparagraph of Article 1(8), the quality, safety and usefulness of the substance which, if used separately, would be considered to be a medicinal product within the meaning of point (2) of Article 1 of Directive 2001/83/EC, shall be verified by analogy with the methods specified in Annex I to Directive 2001/83/EC, as required by the applicable conformity assessment procedure under this Regulation."
    },
    {
        "full_reference": "GSPR 12.2",
        "chapter": "Chapter II",
        "section": "Medicinal products and substances absorbed",
        "text": "Devices that are composed of substances or of combinations of substances that are intended to be introduced into the human body, and that are absorbed by or locally dispersed in the human body shall comply, where applicable and in a manner limited to the aspects not covered by this Regulation, with the relevant requirements laid down in Annex I to Directive 2001/83/EC for the evaluation of absorption, distribution, metabolism, excretion, local tolerance, toxicity, interaction with other devices, medicinal products or other substances and potential for adverse reactions, as required by the applicable conformity assessment procedure under this Regulation."
    },
    {
        "full_reference": "GSPR 13.1",
        "chapter": "Chapter II",
        "section": "Materials of biological origin",
        "text": "For devices manufactured utilising derivatives of tissues or cells of human origin which are non-viable or are rendered non-viable covered by this Regulation in accordance with point (g) of Article 1(6), the following shall apply:",
        "children": [
            {"full_reference": "GSPR 13.1(a)", "chapter": "Chapter II", "section": "Materials of biological origin", "text": "donation, procurement and testing of the tissues and cells shall be done in accordance with Directive 2004/23/EC;"},
            {"full_reference": "GSPR 13.1(b)", "chapter": "Chapter II", "section": "Materials of biological origin", "text": "processing, preservation and any other handling of those tissues and cells or their derivatives shall be carried out so as to provide safety for patients, users and, where applicable, other persons. In particular, safety with regard to viruses and other transmissible agents shall be addressed by appropriate methods of sourcing and by implementation of validated methods of elimination or inactivation in the course of the manufacturing process;"},
            {"full_reference": "GSPR 13.1(c)", "chapter": "Chapter II", "section": "Materials of biological origin", "text": "the traceability system for those devices shall be complementary and compatible with the traceability and data protection requirements laid down in Directive 2004/23/EC and in Directive 2002/98/EC."}
        ]
    },
    {
        "full_reference": "GSPR 13.2",
        "chapter": "Chapter II",
        "section": "Materials of biological origin",
        "text": "For devices manufactured utilising tissues or cells of animal origin, or their derivatives, which are non-viable or rendered non-viable the following shall apply:",
        "children": [
            {"full_reference": "GSPR 13.2(a)", "chapter": "Chapter II", "section": "Materials of biological origin", "text": "where feasible taking into account the animal species, tissues and cells of animal origin, or their derivatives, shall originate from animals that have been subjected to veterinary controls that are adapted to the intended use of the tissues. Information on the geographical origin of the animals shall be retained by manufacturers;"},
            {"full_reference": "GSPR 13.2(b)", "chapter": "Chapter II", "section": "Materials of biological origin", "text": "sourcing, processing, preservation, testing and handling of tissues, cells and substances of animal origin, or their derivatives, shall be carried out so as to provide safety for patients, users and, where applicable, other persons. In particular safety with regard to viruses and other transmissible agents shall be addressed by implementation of validated methods of elimination or viral inactivation in the course of the manufacturing process, except when the use of such methods would lead to unacceptable degradation compromising the clinical benefit of the device;"},
            {"full_reference": "GSPR 13.2(c)", "chapter": "Chapter II", "section": "Materials of biological origin", "text": "in the case of devices manufactured utilising tissues or cells of animal origin, or their derivatives, as referred to in Regulation (EU) No 722/2012 the particular requirements laid down in that Regulation shall apply."}
        ]
    },
    {
        "full_reference": "GSPR 13.3",
        "chapter": "Chapter II",
        "section": "Materials of biological origin",
        "text": "For devices manufactured utilising non-viable biological substances other than those referred to in Sections 13.1 and 13.2, the processing, preservation, testing and handling of those substances shall be carried out so as to provide safety for patients, users and, where applicable, other persons, including in the waste disposal chain. In particular, safety with regard to viruses and other transmissible agents shall be addressed by appropriate methods of sourcing and by implementation of validated methods of elimination or inactivation in the course of the manufacturing process."
    },
    {
        "full_reference": "GSPR 14.1",
        "chapter": "Chapter II",
        "section": "Construction and environment",
        "text": "If the device is intended for use in combination with other devices or equipment the whole combination, including the connection system shall be safe and shall not impair the specified performance of the devices. Any restrictions on use applying to such combinations shall be indicated on the label and/or in the instructions for use. Connections which the user has to handle, such as fluid, gas transfer, electrical or mechanical coupling, shall be designed and constructed in such a way as to minimise all possible risks, such as misconnection."
    },
    {
        "full_reference": "GSPR 14.2",
        "chapter": "Chapter II",
        "section": "Construction and environment",
        "text": "Devices shall be designed and manufactured in such a way as to remove or reduce as far as possible:",
        "children": [
            {"full_reference": "GSPR 14.2(a)", "chapter": "Chapter II", "section": "Construction and environment", "text": "the risk of injury, in connection with their physical features, including the volume/pressure ratio, dimensional and where appropriate ergonomic features;"},
            {"full_reference": "GSPR 14.2(b)", "chapter": "Chapter II", "section": "Construction and environment", "text": "risks connected with reasonably foreseeable external influences or environmental conditions, such as magnetic fields, external electrical and electromagnetic effects, electrostatic discharge, radiation associated with diagnostic or therapeutic procedures, pressure, humidity, temperature, variations in pressure and acceleration or radio signal interferences;"},
            {"full_reference": "GSPR 14.2(c)", "chapter": "Chapter II", "section": "Construction and environment", "text": "the risks associated with the use of the device when it comes into contact with materials, liquids, and substances, including gases, to which it is exposed during normal conditions of use;"},
            {"full_reference": "GSPR 14.2(d)", "chapter": "Chapter II", "section": "Construction and environment", "text": "the risks associated with the possible negative interaction between software and the IT environment within which it operates and interacts;"},
            {"full_reference": "GSPR 14.2(e)", "chapter": "Chapter II", "section": "Construction and environment", "text": "the risks of accidental ingress of substances into the device;"},
            {"full_reference": "GSPR 14.2(f)", "chapter": "Chapter II", "section": "Construction and environment", "text": "the risks of reciprocal interference with other devices normally used in the investigations or for the treatment given; and"},
            {"full_reference": "GSPR 14.2(g)", "chapter": "Chapter II", "section": "Construction and environment", "text": "risks arising where maintenance or calibration are not possible (as with implants), from ageing of materials used or loss of accuracy of any measuring or control mechanism."}
        ]
    },
    {
        "full_reference": "GSPR 14.3",
        "chapter": "Chapter II",
        "section": "Construction and environment",
        "text": "Devices shall be designed and manufactured in such a way as to minimise the risks of fire or explosion during normal use and in single fault condition. Particular attention shall be paid to devices the intended use of which includes exposure to or use in association with flammable or explosive substances or substances which could cause combustion."
    },
    {
        "full_reference": "GSPR 14.4",
        "chapter": "Chapter II",
        "section": "Construction and environment",
        "text": "Devices shall be designed and manufactured in such a way that adjustment, calibration, and maintenance can be done safely and effectively."
    },
    {
        "full_reference": "GSPR 14.5",
        "chapter": "Chapter II",
        "section": "Construction and environment",
        "text": "Devices that are intended to be operated together with other devices or products shall be designed and manufactured in such a way that the interoperability and compatibility are reliable and safe."
    },
    {
        "full_reference": "GSPR 14.6",
        "chapter": "Chapter II",
        "section": "Construction and environment",
        "text": "Any measurement, monitoring or display scale shall be designed and manufactured in line with ergonomic principles, taking account of the intended purpose, users and the environmental conditions in which the devices are intended to be used."
    },
    {
        "full_reference": "GSPR 14.7",
        "chapter": "Chapter II",
        "section": "Construction and environment",
        "text": "Devices shall be designed and manufactured in such a way as to facilitate their safe disposal and the safe disposal of related waste substances by the user, patient or other person. To that end, manufacturers shall identify and test procedures and measures as a result of which their devices can be safely disposed after use. Such procedures shall be described in the instructions for use."
    },
    {
        "full_reference": "GSPR 15.1",
        "chapter": "Chapter II",
        "section": "Diagnostic and measuring function",
        "text": "Diagnostic devices and devices with a measuring function, shall be designed and manufactured in such a way as to provide sufficient accuracy, precision and stability for their intended purpose, based on appropriate scientific and technical methods. The limits of accuracy shall be indicated by the manufacturer."
    },
    {
        "full_reference": "GSPR 15.2",
        "chapter": "Chapter II",
        "section": "Diagnostic and measuring function",
        "text": "The measurements made by devices with a measuring function shall be expressed in legal units conforming to the provisions of Council Directive 80/181/EEC."
    },
    {
        "full_reference": "GSPR 16.1",
        "chapter": "Chapter II",
        "section": "Protection against radiation",
        "text": "Radiation protection requirements:",
        "children": [
            {"full_reference": "GSPR 16.1(a)", "chapter": "Chapter II", "section": "Protection against radiation", "text": "Devices shall be designed, manufactured and packaged in such a way that exposure of patients, users and other persons to radiation is reduced as far as possible, and in a manner that is compatible with the intended purpose, whilst not restricting the application of appropriate specified levels for therapeutic and diagnostic purposes."},
            {"full_reference": "GSPR 16.1(b)", "chapter": "Chapter II", "section": "Protection against radiation", "text": "The operating instructions for devices emitting hazardous or potentially hazardous radiation shall contain detailed information as to the nature of the emitted radiation, the means of protecting the patient and the user, and on ways of avoiding misuse and of reducing the risks inherent to installation as far as possible and appropriate. Information regarding the acceptance and performance testing, the acceptance criteria, and the maintenance procedure shall also be specified."}
        ]
    },
    {
        "full_reference": "GSPR 16.2",
        "chapter": "Chapter II",
        "section": "Protection against radiation",
        "text": "Radiation control requirements:",
        "children": [
            {"full_reference": "GSPR 16.2(a)", "chapter": "Chapter II", "section": "Protection against radiation", "text": "Where devices are designed to emit hazardous, or potentially hazardous, levels of ionizing and/or non- ionizing radiation necessary for a specific medical purpose the benefit of which is considered to outweigh the risks inherent to the emission, it shall be possible for the user to control the emissions. Such devices shall be designed and manufactured to ensure reproducibility of relevant variable parameters within an acceptable tolerance."},
            {"full_reference": "GSPR 16.2(b)", "chapter": "Chapter II", "section": "Protection against radiation", "text": "Where devices are intended to emit hazardous, or potentially hazardous, ionizing and/or non-ionizing radiation, they shall be fitted, where possible, with visual displays and/or audible warnings of such emissions."}
        ]
    },
    {
        "full_reference": "GSPR 16.3",
        "chapter": "Chapter II",
        "section": "Protection against radiation",
        "text": "Devices shall be designed and manufactured in such a way that exposure of patients, users and other persons to the emission of unintended, stray or scattered radiation is reduced as far as possible. Where possible and appropriate, methods shall be selected which reduce the exposure to radiation of patients, users and other persons who may be affected."
    },
    {
        "full_reference": "GSPR 16.4",
        "chapter": "Chapter II",
        "section": "Protection against radiation",
        "text": "Ionizing radiation requirements:",
        "children": [
            {"full_reference": "GSPR 16.4(a)", "chapter": "Chapter II", "section": "Protection against radiation", "text": "Devices intended to emit ionizing radiation shall be designed and manufactured taking into account the requirements of the Directive 2013/59/Euratom laying down basic safety standards for protection against the dangers arising from exposure to ionising radiation."},
            {"full_reference": "GSPR 16.4(b)", "chapter": "Chapter II", "section": "Protection against radiation", "text": "Devices intended to emit ionising radiation shall be designed and manufactured in such a way as to ensure that, where possible, taking into account the intended use, the quantity, geometry and quality of the radiation emitted can be varied and controlled, and, if possible, monitored during treatment."},
            {"full_reference": "GSPR 16.4(c)", "chapter": "Chapter II", "section": "Protection against radiation", "text": "Devices emitting ionising radiation intended for diagnostic radiology shall be designed and manufactured in such a way as to achieve an image and/or output quality that are appropriate to the intended medical purpose whilst minimising radiation exposure of the patient and user."},
            {"full_reference": "GSPR 16.4(d)", "chapter": "Chapter II", "section": "Protection against radiation", "text": "Devices that emit ionising radiation and are intended for therapeutic radiology shall be designed and manufactured in such a way as to enable reliable monitoring and control of the delivered dose, the beam type, energy and, where appropriate, the quality of radiation."}
        ]
    },
    {
        "full_reference": "GSPR 17.1",
        "chapter": "Chapter II",
        "section": "Electronic programmable systems",
        "text": "Devices that incorporate electronic programmable systems, including software, or software that are devices in themselves, shall be designed to ensure repeatability, reliability and performance in line with their intended use. In the event of a single fault condition, appropriate means shall be adopted to eliminate or reduce as far as possible consequent risks or impairment of performance."
    },
    {
        "full_reference": "GSPR 17.2",
        "chapter": "Chapter II",
        "section": "Electronic programmable systems",
        "text": "For devices that incorporate software or for software that are devices in themselves, the software shall be developed and manufactured in accordance with the state of the art taking into account the principles of development life cycle, risk management, including information security, verification and validation."
    },
    {
        "full_reference": "GSPR 17.3",
        "chapter": "Chapter II",
        "section": "Electronic programmable systems",
        "text": "Software referred to in this Section that is intended to be used in combination with mobile computing platforms shall be designed and manufactured taking into account the specific features of the mobile platform (e.g. size and contrast ratio of the screen) and the external factors related to their use (varying environment as regards level of light or noise)."
    },
    {
        "full_reference": "GSPR 17.4",
        "chapter": "Chapter II",
        "section": "Electronic programmable systems",
        "text": "Manufacturers shall set out minimum requirements concerning hardware, IT networks characteristics and IT security measures, including protection against unauthorised access, necessary to run the software as intended."
    },
    {
        "full_reference": "GSPR 18.1",
        "chapter": "Chapter II",
        "section": "Active devices",
        "text": "For non-implantable active devices, in the event of a single fault condition, appropriate means shall be adopted to eliminate or reduce as far as possible consequent risks."
    },
    {
        "full_reference": "GSPR 18.2",
        "chapter": "Chapter II",
        "section": "Active devices",
        "text": "Devices where the safety of the patient depends on an internal power supply shall be equipped with a means of determining the state of the power supply and an appropriate warning or indication for when the capacity of the power supply becomes critical. If necessary, such warning or indication shall be given prior to the power supply becoming critical."
    },
    {
        "full_reference": "GSPR 18.3",
        "chapter": "Chapter II",
        "section": "Active devices",
        "text": "Devices where the safety of the patient depends on an external power supply shall include an alarm system to signal any power failure."
    },
    {
        "full_reference": "GSPR 18.4",
        "chapter": "Chapter II",
        "section": "Active devices",
        "text": "Devices intended to monitor one or more clinical parameters of a patient shall be equipped with appropriate alarm systems to alert the user of situations which could lead to death or severe deterioration of the patient's state of health."
    },
    {
        "full_reference": "GSPR 18.5",
        "chapter": "Chapter II",
        "section": "Active devices",
        "text": "Devices shall be designed and manufactured in such a way as to reduce as far as possible the risks of creating electromagnetic interference which could impair the operation of the device in question or other devices or equipment in the intended environment."
    },
    {
        "full_reference": "GSPR 18.6",
        "chapter": "Chapter II",
        "section": "Active devices",
        "text": "Devices shall be designed and manufactured in such a way as to provide a level of intrinsic immunity to electromagnetic interference such that is adequate to enable them to operate as intended."
    },
    {
        "full_reference": "GSPR 18.7",
        "chapter": "Chapter II",
        "section": "Active devices",
        "text": "Devices shall be designed and manufactured in such a way as to avoid, as far as possible, the risk of accidental electric shocks to the patient, user or any other person, both during normal use of the device and in the event of a single fault condition in the device, provided the device is installed and maintained as indicated by the manufacturer."
    },
    {
        "full_reference": "GSPR 18.8",
        "chapter": "Chapter II",
        "section": "Active devices",
        "text": "Devices shall be designed and manufactured in such a way as to protect, as far as possible, against unauthorised access that could hamper the device from functioning as intended."
    },
    {
        "full_reference": "GSPR 19.1",
        "chapter": "Chapter II",
        "section": "Active implantable devices",
        "text": "Active implantable devices shall be designed and manufactured in such a way as to remove or minimize as far as possible:",
        "children": [
            {"full_reference": "GSPR 19.1(a)", "chapter": "Chapter II", "section": "Active implantable devices", "text": "risks connected with the use of energy sources with particular reference, where electricity is used, to insulation, leakage currents and overheating of the devices,"},
            {"full_reference": "GSPR 19.1(b)", "chapter": "Chapter II", "section": "Active implantable devices", "text": "risks connected with medical treatment, in particular those resulting from the use of defibrillators or high-frequency surgical equipment, and"},
            {"full_reference": "GSPR 19.1(c)", "chapter": "Chapter II", "section": "Active implantable devices", "text": "risks which may arise where maintenance and calibration are impossible, including: — excessive increase of leakage currents, — ageing of the materials used, — excess heat generated by the device, — decreased accuracy of any measuring or control mechanism."}
        ]
    },
    {
        "full_reference": "GSPR 19.2",
        "chapter": "Chapter II",
        "section": "Active implantable devices",
        "text": "Active implantable devices shall be designed and manufactured in such a way as to ensure:",
        "children": [
            {"full_reference": "GSPR 19.2.1", "chapter": "Chapter II", "section": "Active implantable devices", "text": "if applicable, the compatibility of the devices with the substances they are intended to administer, and"},
            {"full_reference": "GSPR 19.2.2", "chapter": "Chapter II", "section": "Active implantable devices", "text": "the reliability of the source of energy."}
        ]
    },
    {
        "full_reference": "GSPR 19.3",
        "chapter": "Chapter II",
        "section": "Active implantable devices",
        "text": "Active implantable devices and, if appropriate, their component parts shall be identifiable to allow any necessary measure to be taken following the discovery of a potential risk in connection with the devices or their component parts."
    },
    {
        "full_reference": "GSPR 19.4",
        "chapter": "Chapter II",
        "section": "Active implantable devices",
        "text": "Active implantable devices shall bear a code by which they and their manufacturer can be unequivocally identified (particularly with regard to the type of device and its year of manufacture); it shall be possible to read this code, if necessary, without the need for a surgical operation."
    },
    {
        "full_reference": "GSPR 20.1",
        "chapter": "Chapter II",
        "section": "Mechanical and thermal risks",
        "text": "Devices shall be designed and manufactured in such a way as to protect patients and users against mechanical risks connected with, for example, resistance to movement, instability and moving parts."
    },
    {
        "full_reference": "GSPR 20.2",
        "chapter": "Chapter II",
        "section": "Mechanical and thermal risks",
        "text": "Devices shall be designed and manufactured in such a way as to reduce to the lowest possible level the risks arising from vibration generated by the devices, taking account of technical progress and of the means available for limiting vibrations, particularly at source, unless the vibrations are part of the specified performance."
    },
    {
        "full_reference": "GSPR 20.3",
        "chapter": "Chapter II",
        "section": "Mechanical and thermal risks",
        "text": "Devices shall be designed and manufactured in such a way as to reduce to the lowest possible level the risks arising from the noise emitted, taking account of technical progress and of the means available to reduce noise, particularly at source, unless the noise emitted is part of the specified performance."
    },
    {
        "full_reference": "GSPR 20.4",
        "chapter": "Chapter II",
        "section": "Mechanical and thermal risks",
        "text": "Terminals and connectors to the electricity, gas or hydraulic and pneumatic energy supplies which the user or other person has to handle, shall be designed and constructed in such a way as to minimise all possible risks."
    },
    {
        "full_reference": "GSPR 20.5",
        "chapter": "Chapter II",
        "section": "Mechanical and thermal risks",
        "text": "Errors likely to be made when fitting or refitting certain parts which could be a source of risk shall be made impossible by the design and construction of such parts or, failing this, by information given on the parts themselves and/or their housings. The same information shall be given on moving parts and/or their housings where the direction of movement needs to be known in order to avoid a risk."
    },
    {
        "full_reference": "GSPR 20.6",
        "chapter": "Chapter II",
        "section": "Mechanical and thermal risks",
        "text": "Accessible parts of devices (excluding the parts or areas intended to supply heat or reach given temperatures) and their surroundings shall not attain potentially dangerous temperatures under normal conditions of use."
    },
    {
        "full_reference": "GSPR 21.1",
        "chapter": "Chapter II",
        "section": "Energy or substance supply",
        "text": "Devices for supplying the patient with energy or substances shall be designed and constructed in such a way that the amount to be delivered can be set and maintained accurately enough to ensure the safety of the patient and of the user."
    },
    {
        "full_reference": "GSPR 21.2",
        "chapter": "Chapter II",
        "section": "Energy or substance supply",
        "text": "Devices shall be fitted with the means of preventing and/or indicating any inadequacies in the amount of energy delivered or substances delivered which could pose a danger. Devices shall incorporate suitable means to prevent, as far as possible, the accidental release of dangerous levels of energy or substances from an energy and/or substance source."
    },
    {
        "full_reference": "GSPR 21.3",
        "chapter": "Chapter II",
        "section": "Energy or substance supply",
        "text": "The function of the controls and indicators shall be clearly specified on the devices. Where a device bears instructions required for its operation or indicates operating or adjustment parameters by means of a visual system, such information shall be understandable to the user and, as appropriate, the patient."
    },
    {
        "full_reference": "GSPR 22.1",
        "chapter": "Chapter II",
        "section": "Lay persons",
        "text": "Devices for use by lay persons shall be designed and manufactured in such a way that they perform appropriately for their intended purpose taking into account the skills and the means available to lay persons and the influence resulting from variation that can be reasonably anticipated in the lay person's technique and environment. The information and instructions provided by the manufacturer shall be easy for the lay person to understand and apply."
    },
    {
        "full_reference": "GSPR 22.2",
        "chapter": "Chapter II",
        "section": "Lay persons",
        "text": "Devices for use by lay persons shall be designed and manufactured in such a way as to:",
        "children": [
            {"full_reference": "GSPR 22.2(a)", "chapter": "Chapter II", "section": "Lay persons", "text": "ensure that the device can be used safely and accurately by the intended user at all stages of the procedure, if necessary after appropriate training and/or information,"},
            {"full_reference": "GSPR 22.2(b)", "chapter": "Chapter II", "section": "Lay persons", "text": "reduce, as far as possible and appropriate, the risk from unintended cuts and pricks such as needle stick injuries, and"},
            {"full_reference": "GSPR 22.2(c)", "chapter": "Chapter II", "section": "Lay persons", "text": "reduce as far as possible the risk of error by the intended user in the handling of the device and, if applicable, in the interpretation of the results."}
        ]
    },
    {
        "full_reference": "GSPR 22.3",
        "chapter": "Chapter II",
        "section": "Lay persons",
        "text": "Devices for use by lay persons shall, where appropriate, include a procedure by which the lay person:",
        "children": [
            {"full_reference": "GSPR 22.3(a)", "chapter": "Chapter II", "section": "Lay persons", "text": "can verify that, at the time of use, the device will perform as intended by the manufacturer, and"},
            {"full_reference": "GSPR 22.3(b)", "chapter": "Chapter II", "section": "Lay persons", "text": "if applicable, is warned if the device has failed to provide a valid result."}
        ]
    },
    # CHAPTER III: REQUIREMENTS REGARDING THE INFORMATION SUPPLIED WITH THE DEVICE
    {
        "full_reference": "GSPR 23.1",
        "chapter": "Chapter III",
        "section": "Label and instructions for use",
        "text": "Each device shall be accompanied by the information needed to identify the device and its manufacturer, and by any safety and performance information relevant to the user, or any other person, as appropriate. Such information may appear on the device itself, on the packaging or in the instructions for use, and shall, if the manufacturer has a website, be made available and kept up to date on the website, taking into account the following:",
        "children": [
            {"full_reference": "GSPR 23.1(a)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "The medium, format, content, legibility, and location of the label and instructions for use shall be appropriate to the particular device, its intended purpose and the technical knowledge, experience, education or training of the intended user(s). In particular, instructions for use shall be written in terms readily understood by the intended user and, where appropriate, supplemented with drawings and diagrams."},
            {"full_reference": "GSPR 23.1(b)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "The information required on the label shall be provided on the device itself. If this is not practicable or appropriate, some or all of the information may appear on the packaging for each unit, and/or on the packaging of multiple devices."},
            {"full_reference": "GSPR 23.1(c)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "Labels shall be provided in a human-readable format and may be supplemented by machine-readable information, such as radio-frequency identification (‘RFID’) or bar codes."},
            {"full_reference": "GSPR 23.1(d)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "Instructions for use shall be provided together with devices. By way of exception, instructions for use shall not be required for class I and class IIa devices if such devices can be used safely without any such instructions and unless otherwise provided for elsewhere in this Section."},
            {"full_reference": "GSPR 23.1(e)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "Where multiple devices are supplied to a single user and/or location, a single copy of the instructions for use may be provided if so agreed by the purchaser who in any case may request further copies to be provided free of charge."},
            {"full_reference": "GSPR 23.1(f)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "Instructions for use may be provided to the user in non-paper format (e.g. electronic) to the extent, and only under the conditions, set out in Regulation (EU) No 207/2012 or in any subsequent implementing rules adopted pursuant to this Regulation."},
            {"full_reference": "GSPR 23.1(g)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "Residual risks which are required to be communicated to the user and/or other person shall be included as limitations, contra-indications, precautions or warnings in the information supplied by the manufacturer."},
            {"full_reference": "GSPR 23.1(h)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "Where appropriate, the information supplied by the manufacturer shall take the form of internationally recognised symbols. Any symbol or identification colour used shall conform to the harmonised standards or CS. In areas for which no harmonised standards or CS exist, the symbols and colours shall be described in the documentation supplied with the device."}
        ]
    },
    {
        "full_reference": "GSPR 23.2",
        "chapter": "Chapter III",
        "section": "Label and instructions for use",
        "text": "The label shall bear all of the following particulars:",
        "children": [
            {"full_reference": "GSPR 23.2(a)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the name or trade name of the device;"},
            {"full_reference": "GSPR 23.2(b)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the details strictly necessary for a user to identify the device, the contents of the packaging and, where it is not obvious for the user, the intended purpose of the device;"},
            {"full_reference": "GSPR 23.2(c)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the name, registered trade name or registered trade mark of the manufacturer and the address of its registered place of business;"},
            {"full_reference": "GSPR 23.2(d)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the manufacturer has its registered place of business outside the Union, the name of the authorised representative and address of the registered place of business of the authorised representative;"},
            {"full_reference": "GSPR 23.2(e)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "where applicable, an indication that the device contains or incorporates: — a medicinal substance, including a human blood or plasma derivative, or — tissues or cells, or their derivatives, of human origin, or — tissues or cells of animal origin, or their derivatives, as referred to in Regulation (EU) No 722/2012;"},
            {"full_reference": "GSPR 23.2(f)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "where applicable, information labelled in accordance with Section 10.4.5.;"},
            {"full_reference": "GSPR 23.2(g)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the lot number or the serial number of the device preceded by the words LOT NUMBER or SERIAL NUMBER or an equivalent symbol, as appropriate;"},
            {"full_reference": "GSPR 23.2(h)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the UDI carrier referred to in Article 27(4) and Part C of Annex VII;"},
            {"full_reference": "GSPR 23.2(i)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "an unambiguous indication of t the time limit for using or implanting the device safely, expressed at least in terms of year and month, where this is relevant;"},
            {"full_reference": "GSPR 23.2(j)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "where there is no indication of the date until when it may be used safely, the date of manufacture. This date of manufacture may be included as part of the lot number or serial number, provided the date is clearly identifiable;"},
            {"full_reference": "GSPR 23.2(k)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "an indication of any special storage and/or handling condition that applies;"},
            {"full_reference": "GSPR 23.2(l)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device is supplied sterile, an indication of its sterile state and the sterilisation method;"},
            {"full_reference": "GSPR 23.2(m)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "warnings or precautions to be taken that need to be brought to the immediate attention of the user of the device, and to any other person. This information may be kept to a minimum in which case more detailed information shall appear in the instructions for use, taking into account the intended users;"},
            {"full_reference": "GSPR 23.2(n)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device is intended for single use, an indication of that fact. A manufacturer's indication of single use shall be consistent across the Union;"},
            {"full_reference": "GSPR 23.2(o)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device is a single-use device that has been reprocessed, an indication of that fact, the number of reprocessing cycles already performed, and any limitation as regards the number of reprocessing cycles;"},
            {"full_reference": "GSPR 23.2(p)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device is custom-made, the words ‘custom-made device’;"},
            {"full_reference": "GSPR 23.2(q)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "an indication that the device is a medical device. If the device is intended for clinical investigation only, the words ‘exclusively for clinical investigation’;"},
            {"full_reference": "GSPR 23.2(r)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "in the case of devices that are composed of substances or of combinations of substances that are intended to be introduced into the human body via a body orifice or applied to the skin and that are absorbed by or locally dispersed in the human body, the overall qualitative composition of the device and quantitative information on the main constituent or constituents responsible for achieving the principal intended action;"},
            {"full_reference": "GSPR 23.2(s)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "for active implantable devices, the serial number, and for other implantable devices, the serial number or the lot number."}
        ]
    },
    {
        "full_reference": "GSPR 23.3",
        "chapter": "Chapter III",
        "section": "Label and instructions for use",
        "text": "The following particulars shall appear on the sterile packaging:",
        "children": [
            {"full_reference": "GSPR 23.3(a)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "an indication permitting the sterile packaging to be recognised as such,"},
            {"full_reference": "GSPR 23.3(b)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "a declaration that the device is in a sterile condition,"},
            {"full_reference": "GSPR 23.3(c)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the method of sterilisation,"},
            {"full_reference": "GSPR 23.3(d)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the name and address of the manufacturer,"},
            {"full_reference": "GSPR 23.3(e)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "a description of the device,"},
            {"full_reference": "GSPR 23.3(f)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device is intended for clinical investigations, the words ‘exclusively for clinical investigations’,"},
            {"full_reference": "GSPR 23.3(g)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device is custom-made, the words ‘custom-made device’,"},
            {"full_reference": "GSPR 23.3(h)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the month and year of manufacture,"},
            {"full_reference": "GSPR 23.3(i)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "an unambiguous indication of the time limit for using or implanting the device safely expressed at least in terms of year and month, and"},
            {"full_reference": "GSPR 23.3(j)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "an instruction to check the instructions for use for what to do if the sterile packaging is damaged or unintentionally opened before use."}
        ]
    },
    {
        "full_reference": "GSPR 23.4",
        "chapter": "Chapter III",
        "section": "Label and instructions for use",
        "text": "The instructions for use shall contain all of the following particulars:",
        "children": [
            {"full_reference": "GSPR 23.4(a)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the particulars referred to in points (a), (c), (e), (f), (k), (l), (n) and (r) of Section 23.2;"},
            {"full_reference": "GSPR 23.4(b)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the device's intended purpose with a clear specification of indications, contra-indications, the patient target group or groups, and of the intended users, as appropriate;"},
            {"full_reference": "GSPR 23.4(c)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "where applicable, a specification of the clinical benefits to be expected."},
            {"full_reference": "GSPR 23.4(d)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "where applicable, links to the summary of safety and clinical performance referred to in Article 32;"},
            {"full_reference": "GSPR 23.4(e)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the performance characteristics of the device;"},
            {"full_reference": "GSPR 23.4(f)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "where applicable, information allowing the healthcare professional to verify if the device is suitable and select the corresponding software and accessories;"},
            {"full_reference": "GSPR 23.4(g)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "any residual risks, contra-indications and any undesirable side-effects, including information to be conveyed to the patient in this regard;"},
            {"full_reference": "GSPR 23.4(h)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "specifications the user requires to use the device appropriately, e.g. if the device has a measuring function, the degree of accuracy claimed for it;"},
            {"full_reference": "GSPR 23.4(i)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "details of any preparatory treatment or handling of the device before it is ready for use or during its use, such as sterilisation, final assembly, calibration, etc., including the levels of disinfection required to ensure patient safety and all available methods for achieving those levels of disinfection;"},
            {"full_reference": "GSPR 23.4(j)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "any requirements for special facilities, or special training, or particular qualifications of the device user and/or other persons;"},
            {"full_reference": "GSPR 23.4(k)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "the information needed to verify whether the device is properly installed and is ready to perform safely and as intended by the manufacturer, together with, where relevant: — details of the nature, and frequency, of preventive and regular maintenance, and of any preparatory cleaning or disinfection, — identification of any consumable components and how to replace them, — information on any necessary calibration to ensure that the device operates properly and safely during its intended lifetime, and — methods for eliminating the risks encountered by persons involved in installing, calibrating or servicing devices;"},
            {"full_reference": "GSPR 23.4(l)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device is supplied sterile, instructions in the event of the sterile packaging being damaged or unintentionally opened before use;"},
            {"full_reference": "GSPR 23.4(m)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device is supplied non-sterile with the intention that it is sterilised before use, the appropriate instructions for sterilisation;"},
            {"full_reference": "GSPR 23.4(n)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device is reusable, information on the appropriate processes for allowing reuse, including cleaning, disinfection, packaging and, where appropriate, the validated method of re-sterilisation appropriate to the Member State or Member States in which the device has been placed on the market. Information shall be provided to identify when the device should no longer be reused, e.g. signs of material degradation or the maximum number of allowable reuses;"},
            {"full_reference": "GSPR 23.4(o)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "an indication, if appropriate, that a device can be reused only if it is reconditioned under the responsibility of the manufacturer to comply with the general safety and performance requirements;"},
            {"full_reference": "GSPR 23.4(p)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device bears an indication that it is for single use, information on known characteristics and technical factors known to the manufacturer that could pose a risk if the device were to be re-used. This information shall be based on a specific section of the manufacturer's risk management documentation, where such characteristics and technical factors shall be addressed in detail. If in accordance with point (d) of Section 23.1. no instructions for use are required, this information shall be made available to the user upon request;"},
            {"full_reference": "GSPR 23.4(q)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "for devices intended for use together with other devices and/or general purpose equipment: — information to identify such devices or equipment, in order to obtain a safe combination, and/or — information on any known restrictions to combinations of devices and equipment;"},
            {"full_reference": "GSPR 23.4(r)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "if the device emits radiation for medical purposes: — detailed information as to the nature, type and where appropriate, the intensity and distribution of the emitted radiation, — the means of protecting the patient, user, or other person from unintended radiation during use of the device;"},
            {"full_reference": "GSPR 23.4(s)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "information that allows the user and/or patient to be informed of any warnings, precautions, contra- indications, measures to be taken and limitations of use regarding the device. That information shall, where relevant, allow the user to brief the patient about any warnings, precautions, contra-indications, measures to be taken and limitations of use regarding the device. The information shall cover, where appropriate: — warnings, precautions and/or measures to be taken in the event of malfunction of the device or changes in its performance that may affect safety, — warnings, precautions and/or measures to be taken as regards the exposure to reasonably foreseeable external influences or environmental conditions, such as magnetic fields, external electrical and electromagnetic effects, electrostatic discharge, radiation associated with diagnostic or therapeutic procedures, pressure, humidity, or temperature, — warnings, precautions and/or measures to be taken as regards the risks of interference posed by the reasonably foreseeable presence of the device during specific diagnostic investigations, evaluations, or therapeutic treatment or other procedures such as electromagnetic interference emitted by the device affecting other equipment, — if the device is intended to administer medicinal products, tissues or cells of human or animal origin, or their derivatives, or biological substances, any limitations or incompatibility in the choice of substances to be delivered, — warnings, precautions and/or limitations related to the medicinal substance or biological material that is incorporated into the device as an integral part of the device; and — precautions related to materials incorporated into the device that contain or consist of CMR substances or endocrine-disrupting substances, or that could result in sensitisation or an allergic reaction by the patient or user;"},
            {"full_reference": "GSPR 23.4(t)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "in the case of devices that are composed of substances or of combinations of substances that are intended to be introduced into the human body and that are absorbed by or locally dispersed in the human body, warnings and precautions, where appropriate, related to the general profile of interaction of the device and its products of metabolism with other devices, medicinal products and other substances as well as contra- indications, undesirable side-effects and risks relating to overdose;"},
            {"full_reference": "GSPR 23.4(u)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "in the case of implantable devices, the overall qualitative and quantitative information on the materials and substances to which patients can be exposed;"},
            {"full_reference": "GSPR 23.4(v)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "warnings or precautions to be taken in order to facilitate the safe disposal of the device, its accessories and the consumables used with it, if any. This information shall cover, where appropriate: — infection or microbial hazards such as explants, needles or surgical equipment contaminated with potentially infectious substances of human origin, and — physical hazards such as from sharps. If in accordance with the point (d) of Section 23.1 no instructions for use are required, this information shall be made available to the user upon request;"},
            {"full_reference": "GSPR 23.4(w)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "for devices intended for use by lay persons, the circumstances in which the user should consult a healthcare professional;"},
            {"full_reference": "GSPR 23.4(x)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "for the devices covered by this Regulation pursuant to Article 1(2), information regarding the absence of a clinical benefit and the risks related to use of the device;"},
            {"full_reference": "GSPR 23.4(y)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "date of issue of the instructions for use or, if they have been revised, date of issue and identifier of the latest revision of the instructions for use;"},
            {"full_reference": "GSPR 23.4(z)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "a notice to the user and/or patient that any serious incident that has occurred in relation to the device should be reported to the manufacturer and the competent authority of the Member State in which the user and/or patient is established;"},
            {"full_reference": "GSPR 23.4(aa)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "information to be supplied to the patient with an implanted device in accordance with Article 18;"},
            {"full_reference": "GSPR 23.4(ab)", "chapter": "Chapter III", "section": "Label and instructions for use", "text": "for devices that incorporate electronic programmable systems, including software, or software that are devices in themselves, minimum requirements concerning hardware, IT networks characteristics and IT security measures, including protection against unauthorised access, necessary to run the software as intended."}
        ]
    }
]

def seed_mdr():
    from app.core.database import engine
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Purge existing data
        print("Purging existing GSPR data to ensure 100% accurate verbatim entries from the latest provided text...")
        db.query(models.GSPRRequirement).delete()
        db.commit()

        print(f"Seeding granular MDR GSPR requirements with hierarchy...")
        
        def add_gspr_recursive(data_list, parent_id=None):
            for req_data in data_list:
                # Extract children if present
                children = req_data.pop("children", [])
                
                # Add current requirement
                db_req = models.GSPRRequirement(**req_data, parent_id=parent_id)
                db.add(db_req)
                db.flush() # Flush to get the ID for children
                
                if children:
                    add_gspr_recursive(children, db_req.id)

        add_gspr_recursive(MDR_GSPR_DATA)
        db.commit()
        print("MDR Annex I Definitive Verbatim Seeding completed successfully.")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_mdr()
