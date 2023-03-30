import os
import re
import csv
from lxml import etree
from zipfile import ZipFile

## Contants: (change these as necessary)
rrOrganizationName: str = "Local Public Health Authority"
os.chdir("./Data Science Projects")

class Address:
    street: str = ""
    city: str = ""
    state: str = ""
    postalCode: str = ""
    county: str = ""
    country: str = ""
    def __init__(self, *args) -> None:
        if len(args) < 1:
            pass
        elif len(args) == 1 and isinstance(args[0], list):
            pass
        elif len(args) == 1 and isinstance(args[0], str):
            pass
        elif len(args) == 1:
            print(f"Warning: single argument provided, but unusable type.\n\tArg: {args[0]}\n\tType: {type(args[0])}")
        else:
            print(f"Warning: multiple arguments provided (all were ignored).\n\tArgs: {', '.join(args)}")
    def toString(self) -> str:
        return(f"{self.street}, {self.city}, {self.state}, {self.postalCode}") # county and country excluded for now


class Person:
    id: str = ""
    fname: str = ""
    mname: str = ""
    lname: str = ""
    birthDate: str = ""
    gender: str = ""
    race: str = ""
    ethnicity: str = ""
    pLanguage: str = ""
    isDead: bool = False
    deathDate: str = ""
    telecomList: list[str] = []
    phones: str = ""
    emails: str = ""
    address: Address = Address() # currently only takes one address, though XML allows multiple
    senderName: str = ""
    senderAddress: Address = Address() # currently only takes one address, though XML allows multiple
    rrContent: etree._Element
    rrReasons1: list[str] = []
    rrReasons2: list[str] = []
    def updateTelecom(self) -> None:
        phones: list[str] = []
        emails: list[str] = []
        for telecom in self.telecomList:
            if telecom.startswith("tel:"):
                phones.append(telecom[4:])
            elif telecom.startswith("mailto:"):
                emails.append(telecom[7:])
        self.phones = ", ".join(phones)
        self.emails = ", ".join(emails)
    def updateRRContent(self) -> None:
        # Clear existing first, as these will be repopulated by self.rrContent
        self.rrReasons1 = []
        self.rrReasons2 = []
        if self.rrContent is not None:
            for content in self.rrContent:
                paragraphs: list[etree._Element] = content.xpath("./paragraph")
                for i in range(len(paragraphs)):
                    try:
                        c: str = paragraphs[i].xpath("./content[1]/text()")[0]
                        if re.search(rrOrganizationName, c) is not None:
                            self.rrReasons1.append(c.split('"')[1])
                            self.rrReasons2.append(paragraphs[i+1].xpath("./text()")[0].split('"')[1])
                            i += 1
                    except:
                        continue
    def toStringHeaders(self) -> str:
        return("\t".join(["ID", "First Name", "Middle Name", "Last Name", "Date of Birth", "Gender", "Race", "Ethnicity", "Preferred Language", "isDead?", "Date of Death", "Phone(s)", "Email(s)", "Address - Street", "Address - City", "Address - State", "Address - Postal Code", "Sender - Name", "Sender - Street", "Sender - City", "Sender - State", "Sender - Postal Code", "RR_Reason1", "RR_Reason2"]))
    def toListHeaders(self) -> list[str]:
        return(["ID", "First Name", "Middle Name", "Last Name", "Date of Birth", "Gender", "Race", "Ethnicity", "Preferred Language", "isDead?", "Date of Death", "Phone(s)", "Email(s)", "Address - Street", "Address - City", "Address - State", "Address - Postal Code", "Sender - Name", "Sender - Street", "Sender - City", "Sender - State", "Sender - Postal Code", "RR_Reason1", "RR_Reason2"])
    def toString(self) -> str:
        return("\t".join([self.id, self.fname, self.mname, self.lname, self.birthDate, self.gender, self.race, self.ethnicity, self.pLanguage, self.isDead, self.deathDate, self.phones, self.emails, self.address.street, self.address.city, self.address.state, self.address.postalCode, self.senderName, self.senderAddress.street, self.senderAddress.city, self.senderAddress.state, self.senderAddress.postalCode, ', '.join(self.rrReasons1), ', '.join(self.rrReasons2)]))
    def toList(self) -> list[str]:
        return([self.id, self.fname, self.mname, self.lname, self.birthDate, self.gender, self.race, self.ethnicity, self.pLanguage, self.isDead, self.deathDate, self.phones, self.emails, self.address.street, self.address.city, self.address.state, self.address.postalCode, self.senderName, self.senderAddress.street, self.senderAddress.city, self.senderAddress.state, self.senderAddress.postalCode, ', '.join(self.rrReasons1), ', '.join(self.rrReasons2)])


def extractXmlPatient(record: etree._Element, record2: etree._Element) -> Person:
    p: Person = Person()

    class Attr:
        numArgs: int = 0
        attribName: str = ""
        path: any = ""
        def update(self, numArgs: int, attribName: str, path: any):
            self.numArgs = numArgs
            self.attribName = attribName
            self.path = path
            return self
    
    attributes: list[Attr] = [
        Attr().update(
            1, 'id', record.xpath('./id/@root')
        ),
        ## alternatively, combine fname and mname into 'givenName' and combine all given names, in case more than 2 occur
        Attr().update(
            1, 'fname', record.xpath('./recordTarget/patientRole/patient/name[@use="L"]/given[1]/text()')
        ),
        Attr().update(
            1, 'mname', record.xpath('./recordTarget/patientRole/patient/name[@use="L"]/given[2]/text()')
        ),
        Attr().update(
            1, 'lname', record.xpath('./recordTarget/patientRole/patient/name[@use="L"]/family/text()')
        ),
        Attr().update(
            1, 'birthDate', record.xpath('./recordTarget/patientRole/patient/birthTime/@value')
        ),
        Attr().update(
            1, 'gender', record.xpath('./recordTarget/patientRole/patient/administrativeGenderCode/@displayName')
        ),
        Attr().update(
            1, 'race', record.xpath('./recordTarget/patientRole/patient/raceCode[1]/@displayName')
        ),
        Attr().update(
            1, 'ethnicity', record.xpath('./recordTarget/patientRole/patient/ethnicGroupCode/@displayName')
        ),
        Attr().update(
            1, 'pLanguage', record.xpath('./recordTarget/patientRole/patient/languageCommunication/languageCode/@code')
        ),
        Attr().update(
            1, 'isDead', record.xpath('./recordTarget/patientRole/patient/deceasedInd/@value')
        ),
        Attr().update(
            1, 'deathDate', record.xpath('./recordTarget/patientRole/patient/deceasedTime/@value')
        ),
        Attr().update(
            -1, 'telecomList', record.xpath('./recordTarget/patientRole/telecom/@value')
        ),
        Attr().update(
            -2, 'address.street', record.xpath('./recordTarget/patientRole/addr[1]/streetAddressLine/text()')
        ),
        Attr().update(
            1, 'address.city', record.xpath('./recordTarget/patientRole/addr[1]/city/text()')
        ),
        Attr().update(
            1, 'address.state', record.xpath('./recordTarget/patientRole/addr[1]/state/text()')
        ),
        Attr().update(
            1, 'address.postalCode', record.xpath('./recordTarget/patientRole/addr[1]/postalCode/text()')
        ),
        Attr().update(
            1, 'senderName', record.xpath('./recordTarget/patientRole/providerOrganization/name/text()')
        ),
        Attr().update(
            -2, 'senderAddress.street', record.xpath('./recordTarget/patientRole/providerOrganization/addr[1]/streetAddressLine/text()')
        ),
        Attr().update(
            1, 'senderAddress.city', record.xpath('./recordTarget/patientRole/providerOrganization/addr[1]/city/text()')
        ),
        Attr().update(
            1, 'senderAddress.state', record.xpath('./recordTarget/patientRole/providerOrganization/addr[1]/state/text()')
        ),
        Attr().update(
            1, 'senderAddress.postalCode', record.xpath('./recordTarget/patientRole/providerOrganization/addr[1]/postalCode/text()')
        ),
        Attr().update(
            # Note that this is in record2 (second xml file, which corresponds to RR)
            -1, 'rrContent', record2.xpath('./component/structuredBody/component[3]/section/text') # assumes this structure is always found in component[3]...
        )
    ]

    for a in attributes:
        if a.path != None:
            listAttr: list[str] = a.attribName.split('.')
            obj: Person = p
            for i in range(len(listAttr)-1):
                obj = obj.__getattribute__(listAttr[i]) # move to child object
            if len(a.path) == a.numArgs:
                if a.numArgs == 1:
                    obj.__setattr__(listAttr[-1], a.path[0])
                elif a.numArgs > 1: ## multiple args, comma-seperated (can change to list if needed)
                    obj.__setattr__(listAttr[-1], ', '.join(a.path))
                else:
                    print(f"Error: Invalid number of arguments in {a.attribName}. Expected {a.numArgs}, but this is not a valid option - check the configuration.") ## should never occur
            elif a.numArgs == -1: ## add as list
                obj.__setattr__(listAttr[-1], a.path)
            elif a.numArgs == -1: ## add as ", "-delimited string
                obj.__setattr__(listAttr[-1], ', '.join(a.path))
            elif len(a.path) == 0:
                pass ## empty - may not be required - use validation to check
            else:
                print(f"Error: Incorrect number of arguments in {a.attribName}. Expected {a.numArgs}, but found {len(a.path)}.")
    p.updateTelecom()
    p.updateRRContent()

    ## Validation
    ## ...

    return p



def unzipFiles(zipDir: str, unzipDir: str) -> None:
    zipFilesList: list[str] = [f for f in os.listdir(zipDir) if str(f).endswith(".zip")]
    for zipFile in zipFilesList:
        with ZipFile((os.sep).join([zipDir,zipFile]), 'r') as z:
            z.extractall((os.sep).join([unzipDir,zipFile])[:-4])

def acquireEcrFileList(xmlRootDir: str, eICRDocument: str, RRDocument: str) -> list[list[str]]:
    xmlSubDirList: list[str] = os.listdir(xmlRootDir)
    ecrXmlFiles: list[str] = [[(os.sep).join([xmlRootDir,x,eICRDocument]), (os.sep).join([xmlRootDir,x,RRDocument])] for x in xmlSubDirList if os.path.isfile((os.sep).join([xmlRootDir,x,eICRDocument])) and os.path.isfile((os.sep).join([xmlRootDir,x,RRDocument]))]
    return(ecrXmlFiles)

def ecrFileListOverride() -> list[list[str]]:
    ## Example of how override can be used (useful for testing if changes need to be made)
    return([
        ["./data/test/eICR_001.xml", "./data/test/RR_001.xml"],
        ["./data/test/eICR_002.xml", "./data/test/RR_002.xml"]
    ])

def processEcrFileList(ecrXmlFiles: list[list[str]], outputFileName: str, delim: str = '\t') -> None:
    with open(outputFileName, 'w') as f:
        fw: csv._writer = csv.writer(f, delimiter=delim, lineterminator='\n')
        fw.writerow(Person().toListHeaders())
        for (xmlFile1, xmlFile2) in ecrXmlFiles:
            xmltree1: etree._ElementTree = etree.parse(xmlFile1)
            root1: etree._Element = xmltree1.getroot()
            xmltree2: etree._ElementTree = etree.parse(xmlFile2)
            root2: etree._Element = xmltree2.getroot()
        #namespace = root.tag[1:].split("}")[0] ## in case capturing namespace is important
        #for record in root.findall('{' + namespace + '}title'):
        #    print(record.text) ## or, you know, do something more useful
        ## (strip all namespaces):
        for element in root1.getiterator():
            if not (isinstance(element, etree._Comment) or isinstance(element, etree._ProcessingInstruction)):
                element.tag = etree.QName(element).localname
        etree.cleanup_namespaces(root1)
        for element in root2.getiterator():
            if not (isinstance(element, etree._Comment) or isinstance(element, etree._ProcessingInstruction)):
                element.tag = etree.QName(element).localname
        etree.cleanup_namespaces(root2)
        fw.writerow(extractXmlPatient(root1, root2).toList())



############ MAIN #############
## Change directories / filenames for the functions as needed.


unzipFiles("./data/zipped", "./data/unzipped")
files: list[list[str]] = acquireEcrFileList("./data/unzipped", "CDA_eICR.xml", "CDA_RR.xml")
#files: list[list[str]] = ecrFileListOverride()
processEcrFileList(files, "output.tsv")
