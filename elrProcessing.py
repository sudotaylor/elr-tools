import os
import re
import csv
from lxml import etree
from zipfile import ZipFile

## Constants: (change these as necessary)
rrOrganizationName: str = "Local Public Health Authority"
os.chdir("./Data Science Projects")

class Address:
    street: str = ""
    city: str = ""
    state: str = ""
    postalCode: str = ""
    county: str = ""    # currently unused
    country: str = ""   # currently unused
    def __init__(self, *args) -> None: # not currently implemented - this would allow an address to be interpreted from different sources (list[str] or string)
        if len(args) < 1:
            pass
        elif len(args) == 1 and isinstance(args[0], list[str]):
            pass
        elif len(args) == 1 and isinstance(args[0], str):
            pass
        elif len(args) == 1:
            print(f"Warning: single argument provided, but unusable type.\n\tArg: {args[0]}\n\tType: {type(args[0])}")
        else:
            print(f"Warning: multiple arguments provided (all were ignored).\n\tArgs: {', '.join(args)}")
    def __repr__(self) -> str: # default string
        return(f"{self.street}, {self.city}, {self.state}, {self.postalCode}") # county and country could also be included
    def toStringLetterFormat(self) -> str: # Just an example of alternative string output
        return(f"{self.street}\n{self.city}, {self.state} {self.postalCode}")


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
    phonesExcelFriendly: str = ""   # leading '+' on phone numbers removed due to issue with default interpretation of CSV in MS Excel (converts '+' to '=' when detecting numeric context)
                                    # Alternatively, another column with the following formula can be added to correct behavior (the original column must remain and appropriate letter assigned to constant "colLetter", rowNumber should be incremented and start at 1):
                                    # "=IF(ISNUMBER(SEARCH(\"=\",FORMULATEXT(" + colLetter + rowNumber + "))),SUBSTITUTE(FORMULATEXT(" + colLetter + rowNumber + "),\"=\",\"+\")," + colLetter + rowNumber + ")"
    emails: str = ""
    address: Address = Address()    # currently only takes one address, though XML allows multiple
    senderName: str = ""
    senderAddress: Address = Address()  # currently only takes one address, though XML allows multiple
    rrContent: etree._Element = None
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
        self.phonesExcelFriendly = ", ".join([(phone[1:] if phone[0]=='+' else phone) for phone in phones])  # strings are arrays :)
        self.emails = ", ".join(emails)
    def updateRRContent(self) -> None:
        # Clear existing first, as these will be repopulated by self.rrContent
        self.rrReasons1 = []
        self.rrReasons2 = []
        if self.rrContent is not None:
            content: re.Match[str] | None = re.search("<paragraph><content.+?>\"(.+?)\".+\"" + rrOrganizationName + "\"\s+?</content></paragraph><paragraph>.+\"(.+?)\"<", str(etree.tostring(self.rrContent))) # may or may not have </br>
            if content is not None:
                self.rrReasons1.append(content.group(1))
                self.rrReasons2.append(content.group(2))
            else:
                print(f"No RR content found for record ({self.id})")
    def toStringHeaders(self, useExcelFriendly: bool = False) -> str:
        if useExcelFriendly:
            ## For now, this displays the same, but it can be modified to indicate Excel-friendly printing
            return("\t".join(["ID", "First Name", "Middle Name", "Last Name", "Date of Birth", "Gender", "Race", "Ethnicity", "Preferred Language", "isDead?", "Date of Death", "Phone(s)", "Email(s)", "Address - Street", "Address - City", "Address - State", "Address - Postal Code", "Sender - Name", "Sender - Street", "Sender - City", "Sender - State", "Sender - Postal Code", "RR_Reason1", "RR_Reason2"]))
        else:
            return("\t".join(["ID", "First Name", "Middle Name", "Last Name", "Date of Birth", "Gender", "Race", "Ethnicity", "Preferred Language", "isDead?", "Date of Death", "Phone(s)", "Email(s)", "Address - Street", "Address - City", "Address - State", "Address - Postal Code", "Sender - Name", "Sender - Street", "Sender - City", "Sender - State", "Sender - Postal Code", "RR_Reason1", "RR_Reason2"]))
    def toListHeaders(self, useExcelFriendly: bool = False) -> list[str]:
        if useExcelFriendly:
            ## For now, this displays the same, but it can be modified to indicate Excel-friendly printing
            return(["ID", "First Name", "Middle Name", "Last Name", "Date of Birth", "Gender", "Race", "Ethnicity", "Preferred Language", "isDead?", "Date of Death", "Phone(s)", "Email(s)", "Address - Street", "Address - City", "Address - State", "Address - Postal Code", "Sender - Name", "Sender - Street", "Sender - City", "Sender - State", "Sender - Postal Code", "RR_Reason1", "RR_Reason2"])
        else:
            return(["ID", "First Name", "Middle Name", "Last Name", "Date of Birth", "Gender", "Race", "Ethnicity", "Preferred Language", "isDead?", "Date of Death", "Phone(s)", "Email(s)", "Address - Street", "Address - City", "Address - State", "Address - Postal Code", "Sender - Name", "Sender - Street", "Sender - City", "Sender - State", "Sender - Postal Code", "RR_Reason1", "RR_Reason2"])
    def toString(self, useExcelFriendly: bool = False) -> str:
        if useExcelFriendly:
            return("\t".join([self.id, self.fname, self.mname, self.lname, self.birthDate, self.gender, self.race, self.ethnicity, self.pLanguage, self.isDead, self.deathDate, self.phonesExcelFriendly, self.emails, self.address.street, self.address.city, self.address.state, self.address.postalCode, self.senderName, self.senderAddress.street, self.senderAddress.city, self.senderAddress.state, self.senderAddress.postalCode, ', '.join(self.rrReasons1), ', '.join(self.rrReasons2)]))
        else:
            return("\t".join([self.id, self.fname, self.mname, self.lname, self.birthDate, self.gender, self.race, self.ethnicity, self.pLanguage, self.isDead, self.deathDate, self.phones, self.emails, self.address.street, self.address.city, self.address.state, self.address.postalCode, self.senderName, self.senderAddress.street, self.senderAddress.city, self.senderAddress.state, self.senderAddress.postalCode, ', '.join(self.rrReasons1), ', '.join(self.rrReasons2)]))
    def toList(self, useExcelFriendly: bool = False) -> list[str]:
        if useExcelFriendly:
            return([self.id, self.fname, self.mname, self.lname, self.birthDate, self.gender, self.race, self.ethnicity, self.pLanguage, self.isDead, self.deathDate, self.phonesExcelFriendly, self.emails, self.address.street, self.address.city, self.address.state, self.address.postalCode, self.senderName, self.senderAddress.street, self.senderAddress.city, self.senderAddress.state, self.senderAddress.postalCode, ', '.join(self.rrReasons1), ', '.join(self.rrReasons2)])
        else:
            return([self.id, self.fname, self.mname, self.lname, self.birthDate, self.gender, self.race, self.ethnicity, self.pLanguage, self.isDead, self.deathDate, self.phones, self.emails, self.address.street, self.address.city, self.address.state, self.address.postalCode, self.senderName, self.senderAddress.street, self.senderAddress.city, self.senderAddress.state, self.senderAddress.postalCode, ', '.join(self.rrReasons1), ', '.join(self.rrReasons2)])

def extractXmlPatient(record: etree._Element, record2: etree._Element) -> Person:
    p: Person = Person()

    class Attribute:
        def __init__(self, numArgs: int = 0, attributeName: str = "", path: any = "") -> None:
            self.numArgs: int = numArgs
            self.attributeName: str = attributeName
            self.path: any = path

    ### Extract XML data and load into object

    ## Select attributes to be used
    attributes: list[Attribute] = [
        Attribute(
            1, 'id', record.xpath('./id/@root')
        ),
        ## alternatively, combine fname and mname into 'givenName' and combine all given names, in case more than 2 occur
        Attribute(
            1, 'fname', record.xpath('./recordTarget/patientRole/patient/name[@use="L"]/given[1]/text()')
        ),
        Attribute(
            1, 'mname', record.xpath('./recordTarget/patientRole/patient/name[@use="L"]/given[2]/text()')
        ),
        Attribute(
            1, 'lname', record.xpath('./recordTarget/patientRole/patient/name[@use="L"]/family/text()')
        ),
        Attribute(
            1, 'birthDate', record.xpath('./recordTarget/patientRole/patient/birthTime/@value')
        ),
        Attribute(
            1, 'gender', record.xpath('./recordTarget/patientRole/patient/administrativeGenderCode/@displayName')
        ),
        Attribute(
            1, 'race', record.xpath('./recordTarget/patientRole/patient/raceCode[1]/@displayName')
        ),
        Attribute(
            1, 'ethnicity', record.xpath('./recordTarget/patientRole/patient/ethnicGroupCode/@displayName')
        ),
        Attribute(
            1, 'pLanguage', record.xpath('./recordTarget/patientRole/patient/languageCommunication/languageCode/@code')
        ),
        Attribute(
            1, 'isDead', record.xpath('./recordTarget/patientRole/patient/deceasedInd/@value')
        ),
        Attribute(
            1, 'deathDate', record.xpath('./recordTarget/patientRole/patient/deceasedTime/@value')
        ),
        Attribute(
            -1, 'telecomList', record.xpath('./recordTarget/patientRole/telecom/@value')
        ),
        Attribute(
            -2, 'address.street', record.xpath('./recordTarget/patientRole/addr[1]/streetAddressLine/text()')
        ),
        Attribute(
            1, 'address.city', record.xpath('./recordTarget/patientRole/addr[1]/city/text()')
        ),
        Attribute(
            1, 'address.state', record.xpath('./recordTarget/patientRole/addr[1]/state/text()')
        ),
        Attribute(
            1, 'address.postalCode', record.xpath('./recordTarget/patientRole/addr[1]/postalCode/text()')
        ),
        Attribute(
            1, 'senderName', record.xpath('./recordTarget/patientRole/providerOrganization/name/text()')
        ),
        Attribute(
            -2, 'senderAddress.street', record.xpath('./recordTarget/patientRole/providerOrganization/addr[1]/streetAddressLine/text()')
        ),
        Attribute(
            1, 'senderAddress.city', record.xpath('./recordTarget/patientRole/providerOrganization/addr[1]/city/text()')
        ),
        Attribute(
            1, 'senderAddress.state', record.xpath('./recordTarget/patientRole/providerOrganization/addr[1]/state/text()')
        ),
        Attribute(
            1, 'senderAddress.postalCode', record.xpath('./recordTarget/patientRole/providerOrganization/addr[1]/postalCode/text()')
        ),
        Attribute(
            # Note that this is in record2 (second xml file, which corresponds to RR)
            1, 'rrContent', record2.xpath('./component/structuredBody/component[3]/section/text')  # assumes this structure is constant
        )
    ]

    ## Populate Person object with attributes
    for a in attributes:
        if a.path != None:
            attributeExpandedList: list[str] = a.attributeName.split('.')
            obj: Person = p
            for i in range(len(attributeExpandedList)-1):
                obj = obj.__getattribute__(attributeExpandedList[i]) # move to child object
            if len(a.path) == a.numArgs:
                if a.numArgs == 1:
                    obj.__setattr__(attributeExpandedList[-1], a.path[0])
                elif a.numArgs > 1: # multiple args, comma-seperated (can change to list if needed)
                    obj.__setattr__(attributeExpandedList[-1], ", ".join(a.path))
                else:
                    print(f"Error: Invalid number of arguments in {a.attributeName}. Expected {a.numArgs}, but this is not a valid option - check the configuration.") ## should never occur
            elif a.numArgs == -1:   # add as list
                obj.__setattr__(attributeExpandedList[-1], a.path)
            elif a.numArgs == -2:   # add as ", "-delimited string
                obj.__setattr__(attributeExpandedList[-1], ", ".join([str(x) for x in a.path]))
            elif len(a.path) == 0:
                pass    # empty - may not be required - use validation to check
            else:
                print(f"Error: Incorrect number of arguments in {a.attributeName}. Expected {a.numArgs}, but found {len(a.path)}.")
    p.updateTelecom()
    p.updateRRContent()

    ### Validation / Transform

    ## birthDate:
    if not re.match(r'^\d{8}$', p.birthDate):   # validate: format should be in "YYYYMMDD"
        print(f"FATAL ERROR: Invalid date format found.\n\tPerson ID: {p.id}\n\tDOB: {p.birthDate}\n")
        exit(1)
    p.birthDate = re.sub(r'^(\d{4})(\d{2})(\d{2})$', r'\2-\3-\1', p.birthDate)   # transform

    ## isDead & deathDate:
    if p.isDead == "false":
        p.isDead = False
    elif p.isDead == "true":
        p.isDead = True
        if p.deathDate == None:
            print("Invalid information: If patient is dead, death date must be specified.")

    ## ... (add further validation rules / data transformations here)

    return p



def unzipFiles(zipDir: str, unzipDir: str) -> None:
    zipFilesList: list[str] = [f for f in os.listdir(zipDir) if str(f).endswith(".zip")]
    for zipFile in zipFilesList:
        with ZipFile((os.sep).join([zipDir,zipFile]), 'r') as z:
            z.extractall((os.sep).join([unzipDir,zipFile])[:-4])

def acquireEcrFileList(xmlRootDir: str, eICRDocument: str, rrDocument: str) -> list[list[str]]:
    xmlSubDirList: list[str] = os.listdir(xmlRootDir)
    ecrXmlFiles: list[str] = [[(os.sep).join([xmlRootDir,x,eICRDocument]), (os.sep).join([xmlRootDir,x,rrDocument])] for x in xmlSubDirList if os.path.isfile((os.sep).join([xmlRootDir,x,eICRDocument])) and os.path.isfile((os.sep).join([xmlRootDir,x,rrDocument]))]
    return(ecrXmlFiles)

def ecrFileListOverride() -> list[list[str]]:
    ## Example of how override can be used (useful for testing if changes need to be made)
    return([
        ["./data/test/eICR_001.xml", "./data/test/RR_001.xml"],
        ["./data/test/eICR_002.xml", "./data/test/RR_002.xml"]
    ])

def processEcrFileList(ecrXmlFiles: list[list[str]], outputFileName: str, delim: str = ',', useExcelFriendly: bool = False) -> None:
    with open(outputFileName, 'w') as f:
        fw: csv._writer = csv.writer(f, delimiter=delim, lineterminator='\n')
        fw.writerow(Person().toListHeaders(useExcelFriendly))
        for (xmlFile1, xmlFile2) in ecrXmlFiles:
            xmltree1: etree._ElementTree = etree.parse(xmlFile1)
            root1: etree._Element = xmltree1.getroot()
            xmltree2: etree._ElementTree = etree.parse(xmlFile2)
            root2: etree._Element = xmltree2.getroot()
        ## (strip all namespaces):
        for element in root1.getiterator():
            if not (isinstance(element, etree._Comment) or isinstance(element, etree._ProcessingInstruction)):
                element.tag = etree.QName(element).localname
        etree.cleanup_namespaces(root1)
        for element in root2.getiterator():
            if not (isinstance(element, etree._Comment) or isinstance(element, etree._ProcessingInstruction)):
                element.tag = etree.QName(element).localname
        etree.cleanup_namespaces(root2)
        fw.writerow(extractXmlPatient(root1, root2).toList(useExcelFriendly))



############ MAIN #############
## Change directories / filenames for the functions as needed.


unzipFiles("./data/zipped", "./data/unzipped")
files: list[list[str]] = acquireEcrFileList("./data/unzipped", "CDA_eICR.xml", "CDA_RR.xml")
#files: list[list[str]] = ecrFileListOverride()
#processEcrFileList(files, "output.tsv", '\t')
processEcrFileList(files, "output.csv", ',', True)
