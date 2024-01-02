<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade - B.1 Part)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 4
		Author:		Laurent DESQUEPER (EU)

		Version:		1.0
		Date:			20/10/2015
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of ICH CodeSystemVersion and EU specific data fields
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif">

	
	<xsl:include href="upgrade-a5.xsl"/>
	<xsl:include href="upgrade-b2.xsl"/>
	<xsl:include href="upgrade-b3.xsl"/>
	<xsl:include href="upgrade-b4.xsl"/>
	<xsl:include href="upgrade-b5.xsl"/>

	<!-- Patient (identification) : 
	E2B(R2): element "patient"
	E2B(R3): element "primaryRole"
	-->
	<xsl:template match="patient" mode="identification">
		<component typeCode="COMP">
			<adverseEventAssessment classCode="INVSTG" moodCode="EVN">
				<subject1 typeCode="SBJ">
					<primaryRole classCode="INVSBJ">
						<player1 classCode="PSN" determinerCode="INSTANCE">
							<!-- B.1.1 Patient Name - Rule LEN-13 -->
							<name>
								<xsl:choose>
									<xsl:when test="translate(patientinitial, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') = 'PRIVACY'"><xsl:attribute name="nullFlavor">MSK</xsl:attribute></xsl:when>
									<xsl:when test="translate(patientinitial, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') = 'UNKNOWN'"><xsl:attribute name="nullFlavor">UNK</xsl:attribute></xsl:when>
									<xsl:when test="string-length(patientinitial) = 0"><xsl:attribute name="nullFlavor">UNK</xsl:attribute></xsl:when>
									<xsl:otherwise><xsl:value-of select="patientinitial"/></xsl:otherwise>
								</xsl:choose>
							</name>
							<!-- B.1.5 Patient Sex -->
							<xsl:choose>
								<xsl:when test="string-length(patientsex) > 0"><administrativeGenderCode code="{patientsex}" codeSystem="{$oidGenderCode}"/></xsl:when>
								<xsl:otherwise><administrativeGenderCode nullFlavor="UNK"/></xsl:otherwise>
							</xsl:choose>
							<!-- B.1.2.1 Patient Birth Time -->
							<xsl:if test="string-length(patientbirthdate) > 0"><birthTime value="{patientbirthdate}"/></xsl:if>
							<!-- B.1.9.1 Date of Death -->
							<xsl:if test="string-length(patientdeath/patientdeathdate) > 0">
								<deceasedTime value="{patientdeath/patientdeathdate}"/>
							</xsl:if>
							<!-- B.1.1.1a Patient GP Medical Record Number -->
							<xsl:if test="string-length(patientgpmedicalrecordnumb) > 0">
								<asIdentifiedEntity classCode="IDENT">
									<id extension="{patientgpmedicalrecordnumb}" root="{$oidGPMedicalRecordNumber}"/>
									<code code="{$GPMrn}" codeSystem="{$oidSourceMedicalRecord}"/>
								</asIdentifiedEntity>
							</xsl:if>
							<!-- B.1.1.1b Patient Specialist Record Number -->
							<xsl:if test="string-length(patientspecialistrecordnumb) > 0">
								<asIdentifiedEntity classCode="IDENT">
									<id extension="{patientspecialistrecordnumb}" root="{$oidSpecialistRecordNumber}"/>
									<code code="{$SpecialistMrn}" codeSystem="{$oidSourceMedicalRecord}"/>
								</asIdentifiedEntity>
							</xsl:if>
							<!-- B.1.1.1c Patient Hospital Record Number -->
							<xsl:if test="string-length(patienthospitalrecordnumb) > 0">
								<asIdentifiedEntity classCode="IDENT">
									<id extension="{patienthospitalrecordnumb}" root="{$oidHospitalRecordNumber}"/>
									<code code="{$HospitalMrn}" codeSystem="{$oidSourceMedicalRecord}"/>
								</asIdentifiedEntity>
							</xsl:if>
							<!-- B.1.1.1d Patient Investigation Number -->
							<xsl:if test="string-length(patientinvestigationnumb) > 0">
								<asIdentifiedEntity classCode="IDENT">
									<id extension="{patientinvestigationnumb}" root="{$oidInvestigationNumber}"/>
									<code code="{$Investigation}" codeSystem="{$oidSourceMedicalRecord}"/>
								</asIdentifiedEntity>
							</xsl:if>
							<!-- B.1.10 - Parent -->
							<xsl:apply-templates select="parent" mode="identification"/>
						</player1>
						<!-- A.5 - Study -->
						<xsl:apply-templates select="../primarysource" mode="study"/>
						<!-- B.1 - Patient -->
						<xsl:apply-templates select="." mode="characteristics"/>
						<!-- B.1.7 - Patient Medical History -->
						<xsl:if test="count(medicalhistoryepisode) > 0 or string-length(patientmedicalhistorytext) > 0">
							<subjectOf2 typeCode="SBJ">
								<organizer classCode="CATEGORY" moodCode="EVN">
									<code code="{$RelevantMedicalHistoryAndConcurrentConditions}" codeSystem="{$oidValueGroupingCode}"/>
									<xsl:apply-templates select="medicalhistoryepisode"/>
									<xsl:if test="string-length(patientmedicalhistorytext) > 0">
										<component typeCode="COMP">
											<observation moodCode="EVN" classCode="OBS">
												<code code="{$HistoryAndConcurrentConditionText}" codeSystem="{$oidObservationCode}"/>
												<value xsi:type="ED" mediaType="text/plain"><xsl:value-of select="patientmedicalhistorytext"/></value>
											</observation>
										</component>
									</xsl:if>
								</organizer>
							</subjectOf2>
						</xsl:if>
						<!-- B.1.8 - Patient Past Drug Therapy -->
						<xsl:if test="count(patientpastdrugtherapy) > 0">
							<subjectOf2 typeCode="SBJ">
								<organizer classCode="CATEGORY" moodCode="EVN">
									<code code="{$DrugHistory}" codeSystem="{$oidValueGroupingCode}"/>
									<xsl:apply-templates select="patientpastdrugtherapy"/>
								</organizer>
							</subjectOf2>
						</xsl:if>
						<!-- B.1.9 - Patient Death -->
						<xsl:apply-templates select="patientdeath"/>
						<!-- B.2.i - Reaction -->
						<xsl:apply-templates select="reaction"/>
						<!-- B.3.r - Test -->
						<xsl:if test="string-length(test/testdate) > 0 or string-length(test/testname) > 0 or string-length(resultstestsprocedures) > 0">
							<subjectOf2 typeCode="SBJ">
								<organizer classCode="CATEGORY" moodCode="EVN">
									<code code="{$TestsAndProceduresRelevantToTheInvestigation}" codeSystem="{$oidValueGroupingCode}"/>
										<xsl:apply-templates select="test"/>
										<xsl:apply-templates select="resultstestsprocedures"/>
								</organizer>
							</subjectOf2>
						</xsl:if>
						
						<!-- B.4.k - Drug (main) -->
						<subjectOf2 typeCode="SBJ">
							<organizer classCode="CATEGORY" moodCode="EVN">
								<code code="{$DrugInformation}" codeSystem="{$oidValueGroupingCode}"/>
								<xsl:apply-templates select="drug" mode="main"/>
							</organizer>
						</subjectOf2>
					</primaryRole>
				</subject1>
				<!-- B.4.k - Drug (causality) -->
						<xsl:apply-templates select="drug" mode="causality"/>
				<!-- B.5 - Summary -->
				<xsl:apply-templates select="summary"/>
			</adverseEventAssessment>
		</component>
	</xsl:template>
	
	<!-- Parent (identification) : 
	E2B(R2): element "parent"
	E2B(R3): element "role"
	-->
	<xsl:template match="parent" mode="identification">
		<xsl:if test="string-length(parentidentification) > 0 or string-length(parentbirthdate) > 0 or string-length(parentsex) > 0 or string-length(parentage) > 0">
		<role classCode="PRS">
			<code code="{$Parent}" codeSystem="2.16.840.1.113883.5.111"/>
				<associatedPerson determinerCode="INSTANCE" classCode="PSN">
					<!-- B.1.10.1 Parent Identification - Rule COD-21-->
					<xsl:if test="string-length(parentidentification) > 0">
						<name>
							<xsl:choose>
								<xsl:when test="translate(parentidentification, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')= 'PRIVACY'"><xsl:attribute name="nullFlavor">MSK</xsl:attribute></xsl:when>
								<xsl:when test="translate(parentidentification, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') = 'UNKNOWN'"><xsl:attribute name="nullFlavor">UNK</xsl:attribute></xsl:when>
								<xsl:otherwise><xsl:value-of select="parentidentification"/></xsl:otherwise>
							</xsl:choose>
						</name>
					</xsl:if>
					<!-- B.1.10.6	Sex of Parent -->
					<xsl:if test="string-length(parentsex) > 0">
						<administrativeGenderCode code="{parentsex}" codeSystem="{$oidGenderCode}"/>
					</xsl:if>
					<!-- B.1.10.2.1	Date of Birth of Parent -->
					<xsl:if test="string-length(parentbirthdate) > 0">
						<birthTime value="{parentbirthdate}"/>
					</xsl:if>
				</associatedPerson>
			
			<!-- B.1.10.2.2	Age of Parent -->
			<xsl:if test="string-length(parentage) > 0">
				<subjectOf2 typeCode="SBJ">
					<observation moodCode="EVN" classCode="OBS">
						<code code="{$Age}" codeSystem="{$oidObservationCode}"/>
						<value xsi:type="PQ" value="{parentage}">
							<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="parentageunit"/></xsl:call-template></xsl:attribute>
						</value>
					</observation>
				</subjectOf2>
			</xsl:if>
			<!-- B.1.10.4 Weight -->
			<xsl:if test="string-length(parentweight) > 0">
				<subjectOf2 typeCode="SBJ">
					<observation moodCode="EVN" classCode="OBS">
						<code code="{$BodyWeight}" codeSystem="{$oidObservationCode}"/>
						<value xsi:type="PQ" value="{parentweight}" unit="kg"/>
					</observation>
				</subjectOf2>
			</xsl:if>
			<!-- B.1.10.5 Height -->
			<xsl:if test="string-length(parentheight) > 0">
				<subjectOf2 typeCode="SBJ">
					<observation moodCode="EVN" classCode="OBS">
						<code code="{$Height}" codeSystem="{$oidObservationCode}"/>
						<value xsi:type="PQ" value="{parentheight}" unit="cm"/>
					</observation>
				</subjectOf2>
			</xsl:if>
			<!-- B.1.10.3 Last Menstrual Period Date -->
			<xsl:if test="string-length(parentlastmenstrualdate) > 0">
				<subjectOf2 typeCode="SBJ">
					<observation moodCode="EVN" classCode="OBS">
						<code code="{$LastMenstrualPeriodDate}" codeSystem="{$oidObservationCode}"/>
						<value xsi:type="TS" value="{parentlastmenstrualdate}"/>
					</observation>
				</subjectOf2>
			</xsl:if>
			<!-- B.1.10.7 - Parent Medical History -->
			<xsl:if test="parentmedicalhistoryepisode">
				<subjectOf2 typeCode="SBJ">
					<organizer classCode="CATEGORY" moodCode="EVN">
						<code code="{$RelevantMedicalHistoryAndConcurrentConditions}" codeSystem="{$oidValueGroupingCode}"/>
						<!-- B.1.10.7.1.r - Parent Medical History -->
						<xsl:apply-templates select="parentmedicalhistoryepisode"/>
						<!-- B.1.10.7.2 - Text for Relevant Medical History and Concurrent Condition of Parent -->
						<xsl:if test="string-length(parentmedicalrelevanttext) > 0">
							<component typeCode="COMP">
								<observation moodCode="EVN" classCode="OBS">
									<code code="{$HistoryAndConcurrentConditionText}" codeSystem="{$oidObservationCode}"/>
									<value xsi:type="ED" mediaType="text/plain"><xsl:value-of select="parentmedicalrelevanttext"/></value>
								</observation>
							</component>
						</xsl:if>
					</organizer>
				</subjectOf2>
			</xsl:if>
			<!-- B.1.10.8.r Past Drug Therapy -->
			<xsl:if test="parentpastdrugtherapy">
				<subjectOf2 typeCode="SBJ">
					<organizer classCode="CATEGORY" moodCode="EVN">
						<code code="{$DrugHistory}" codeSystem="{$oidValueGroupingCode}"/>
						<xsl:apply-templates select="parentpastdrugtherapy"/>
					</organizer>
				</subjectOf2>
			</xsl:if>
		</role>
		</xsl:if>
	</xsl:template>

	<!-- Parent (medical history episode) : 
	E2B(R2): element "parentmedicalhistoryepisode"
	E2B(R3): element "role"
	-->
	<xsl:template match="parentmedicalhistoryepisode">
		<component typeCode="COMP">
			<observation moodCode="EVN" classCode="OBS">
				<!-- B.1.10.7.1r.a Disease / Surgical Procedure/ etc. -->
				<xsl:variable name="isMeddraCode">
					<xsl:call-template name="isMeddraCode">
						<xsl:with-param name="code" select="parentmedicalepisodename"/>
					</xsl:call-template>
				</xsl:variable>
				<xsl:choose>
					<xsl:when test="$isMeddraCode = 'yes'">
						<code code="{parentmedicalepisodename}" codeSystemVersion="{parentmdepisodemeddraversion}" codeSystem="{$oidMedDRA}"/>
					</xsl:when>
					<xsl:otherwise>
						<code>
							<originalText>
								<xsl:value-of select="parentmedicalepisodename"/>
								<xsl:if test="string-length(parentmdepisodemeddraversion) > 0"> (<xsl:value-of select="parentmdepisodemeddraversion"/>)</xsl:if>
							</originalText>
						</code>
					</xsl:otherwise>
				</xsl:choose>
				<!-- B.1.10.7.1r.cd Start Date and End Date -->
				<xsl:if test="string-length(parentmedicalstartdate) > 0 or string-length(parentmedicalenddate) > 0">
					<effectiveTime xsi:type="IVL_TS">
						<xsl:if test="string-length(parentmedicalstartdate) > 0"><low value="{parentmedicalstartdate}"/></xsl:if>
						<xsl:if test="string-length(parentmedicalenddate) > 0"><high value="{parentmedicalenddate}"/></xsl:if>
					</effectiveTime>
				</xsl:if>
				<!-- B.1.10.7.1r.g Comments  -->
				<xsl:if test="string-length(parentmedicalcomment) > 0">
					<outboundRelationship2 typeCode="COMP">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$Comment}" codeSystem="{$oidObservationCode}"/>
							<value xsi:type="ED"><xsl:value-of select="parentmedicalcomment"/></value>
						</observation>
					</outboundRelationship2>
				</xsl:if>
				<!-- B.1.10.7.1.r.f - Continuing -->
				<xsl:if test="parentmedicalcontinue = 1 or parentmedicalcontinue = 2 or parentmedicalcontinue = 3">
					<inboundRelationship typeCode="REFR">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$Continuing}"  codeSystem="{$oidObservationCode}"/>
							<xsl:choose>
								<xsl:when test="parentmedicalcontinue = 1"><value xsi:type="BL" value="true"/></xsl:when>
								<xsl:when test="parentmedicalcontinue = 2"><value xsi:type="BL" value="false"/></xsl:when>
								<xsl:when test="parentmedicalcontinue = 3"><value xsi:type="BL" nullFlavor="NASK" /></xsl:when>
							</xsl:choose>
						</observation>
					</inboundRelationship>
				</xsl:if>
			</observation>
		</component>
	</xsl:template>

	<!-- Parent (past drug therapy) : 
	E2B(R2): element "parentpastdrugtherapy"
	E2B(R3): element "role"
	-->
	<xsl:template match="parentpastdrugtherapy">
		<component typeCode="COMP">
			<substanceAdministration moodCode="EVN" classCode="SBADM">
				<xsl:if test="string-length(parentdrugstartdate) > 0 or string-length(parentdrugenddate) > 0">
					<effectiveTime xsi:type="IVL_TS">
						<xsl:if test="string-length(parentdrugstartdate) > 0">
							<!-- B.1.10.8.r.c - Parent Drug Start Date -->
							<low value="{parentdrugstartdate}"/>
						</xsl:if>
						<xsl:if test="string-length(parentdrugenddate) > 0">
							<!-- B.1.10.8.r.e - Parent Drug End Date -->
							<high value="{parentdrugenddate}"/>
						</xsl:if>
					</effectiveTime>
				</xsl:if>
				<xsl:if test="string-length(parentdrugname) > 0">
					<consumable typeCode="CSM">
						<instanceOfKind classCode="INST">
							<kindOfProduct classCode="MMAT" determinerCode="KIND">
								<code/>
								<!-- B.1.10.8.r.a0	Name of Drug as Reported -->
								<name><xsl:value-of select="parentdrugname"/></name>
							</kindOfProduct>
						</instanceOfKind>
					</consumable>
				</xsl:if>
				<xsl:if test="string-length(parentdrugindication) > 0">
					<outboundRelationship2 typeCode="RSON">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$Indication}" codeSystem="{$oidObservationCode}"/>
							<!-- B.1.10.8.r.f1/2 Indication -->
							<xsl:variable name="isIndicationMeddraCode">
								<xsl:call-template name="isMeddraCode">
									<xsl:with-param name="code" select="parentdrugindication"/>
								</xsl:call-template>
							</xsl:variable>
							<xsl:choose>
								<xsl:when test="$isIndicationMeddraCode = 'yes'">
									<value xsi:type="CE" code="{parentdrugindication}" codeSystemVersion="{parentdrgindicationmeddraversion}" codeSystem="{$oidMedDRA}"/>
								</xsl:when>
								<xsl:otherwise>
									<value xsi:type="CE">
										<originalText>
											<xsl:value-of select="parentdrugindication"/>
											<xsl:if test="string-length(parentdrgindicationmeddraversion) > 0"> (<xsl:value-of select="parentdrgindicationmeddraversion"/>)</xsl:if>
										</originalText>
									</value>
								</xsl:otherwise>
							</xsl:choose>
						</observation>
					</outboundRelationship2>
				</xsl:if>
				<xsl:if test="string-length(parentdrugreaction) > 0">
					<outboundRelationship2 typeCode="CAUS">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$Reaction}" codeSystem="{$oidObservationCode}"/>
							<!-- B.1.10.8.r.g1/2 Reaction -->
							<xsl:variable name="isReractionMeddraCode">
								<xsl:call-template name="isMeddraCode">
									<xsl:with-param name="code" select="parentdrugreaction"/>
								</xsl:call-template>
							</xsl:variable>
							<xsl:choose>
								<xsl:when test="$isReractionMeddraCode = 'yes'">
									<value xsi:type="CE" code="{parentdrugreaction}" codeSystemVersion="{parentdrgreactionmeddraversion}" codeSystem="{$oidMedDRA}"/>
								</xsl:when>
								<xsl:otherwise>
									<value xsi:type="CE">
										<originalText>
											<xsl:value-of select="parentdrugreaction"/>
											<xsl:if test="string-length(parentdrgreactionmeddraversion) > 0"> (<xsl:value-of select="parentdrgreactionmeddraversion"/>)</xsl:if>
										</originalText>
									</value>
								</xsl:otherwise>
							</xsl:choose>
						</observation>
					</outboundRelationship2>
				</xsl:if>
			</substanceAdministration>
		</component>
	</xsl:template>
	
		<!-- Patient (characteristics) : 
	E2B(R2): element "patient"
	E2B(R3): element "primaryRole"
	-->
	<xsl:template match="patient" mode="characteristics">
		<!-- B.1.2.2.ab Age at time of onset of reaction/event - Rule COD-10 -->
		<xsl:if test="string-length(patientonsetage) > 0">
			<subjectOf2 typeCode="SBJ">
				<observation moodCode="EVN" classCode="OBS">
					<code code="{$Age}" codeSystem="{$oidObservationCode}"/>
					<value xsi:type="PQ" value="{patientonsetage}">
						<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="patientonsetageunit"/></xsl:call-template></xsl:attribute>
					</value>
				</observation>
			</subjectOf2>
		</xsl:if>
		<!-- B.1.2.2.1.ab Gestation Period -->
		<xsl:if test="string-length(gestationperiod) > 0">
			<subjectOf2 typeCode="SBJ">
				<observation moodCode="EVN" classCode="OBS">
					<code code="{$GestationPeriod}" codeSystem="{$oidObservationCode}"/>
					<value xsi:type="PQ" value="{gestationperiod}">
						<xsl:attribute name="unit"><xsl:call-template name="getMapping"><xsl:with-param name="type">UCUM</xsl:with-param><xsl:with-param name="code" select="gestationperiodunit"/></xsl:call-template></xsl:attribute>
					</value>
				</observation>
			</subjectOf2>
		</xsl:if>	
		<!-- B.1.2.3. Age Group -->
		<xsl:if test="string-length(patientagegroup) > 0">
			<subjectOf2 typeCode="SBJ">
				<observation moodCode="EVN" classCode="OBS">
					<code code="{$AgeGroup}" codeSystem="{$oidObservationCode}"/>
					<value xsi:type="CE" code="{patientagegroup}" codeSystem="{$oidAgeGroup}" codeSystemVersion="{$oidAgeGroupCSV}"/>
				</observation>
			</subjectOf2>
		</xsl:if>
		<!-- B.1.3. Body Weight -->
		<xsl:if test="string-length(patientweight) > 0">
			<subjectOf2 typeCode="SBJ">
				<observation moodCode="EVN" classCode="OBS">
					<code code="{$BodyWeight}" codeSystem="{$oidObservationCode}"/>
					<value xsi:type="PQ" value="{patientweight}" unit="kg"/>
				</observation>
			</subjectOf2>
		</xsl:if>
		<!-- B.1.4 Height -->
		<xsl:if test="string-length(patientheight) > 0">
			<subjectOf2 typeCode="SBJ">
				<observation moodCode="EVN" classCode="OBS">
					<code code="{$Height}" codeSystem="{$oidObservationCode}"/>
					<value xsi:type="PQ" value="{patientheight}" unit="cm"/>
				</observation>
			</subjectOf2>
		</xsl:if>
		<!-- B.1.6 Last Menstrual Period Date -->
		<xsl:if test="string-length(patientlastmenstrualdate) > 0">
			<subjectOf2 typeCode="SBJ">
				<observation moodCode="EVN" classCode="OBS">
					<code code="{$LastMenstrualPeriodDate}" codeSystem="{$oidObservationCode}"/>
					<value xsi:type="TS" value="{patientlastmenstrualdate}"/>
				</observation>
			</subjectOf2>
		</xsl:if>
	</xsl:template>
	
	<!-- Patient (medical history episode) : 
	E2B(R2): element "medicalhistoryepisode"
	E2B(R3): element "primaryRole"
	-->
	<xsl:template match="medicalhistoryepisode">
		<component typeCode="COMP">
			<observation moodCode="EVN" classCode="OBS">
				<!-- B.1.7.1r.a Disease / Surgical Procedure/ etc. -->
				<xsl:variable name="isMeddraCode">
					<xsl:call-template name="isMeddraCode">
						<xsl:with-param name="code" select="patientepisodename"/>
					</xsl:call-template>
				</xsl:variable>
				<xsl:choose>
					<xsl:when test="$isMeddraCode = 'yes'">
						<code code="{patientepisodename}" codeSystemVersion="{patientepisodenamemeddraversion}" codeSystem="{$oidMedDRA}"/>
					</xsl:when>
					<xsl:otherwise>
						<code>
							<originalText>
								<xsl:value-of select="patientepisodename"/>
								<xsl:if test="string-length(patientepisodenamemeddraversion) > 0"> (<xsl:value-of select="patientepisodenamemeddraversion"/>)</xsl:if>
							</originalText>
						</code>
					</xsl:otherwise>
				</xsl:choose>
				<!-- B.1.7.1r.cdf Start Date and End Date -->
				<xsl:if test="string-length(patientmedicalstartdate) > 0 or string-length(patientmedicalenddate) > 0">
					<effectiveTime xsi:type="IVL_TS">
						<xsl:if test="string-length(patientmedicalstartdate) > 0"><low value="{patientmedicalstartdate}"/></xsl:if>
						<xsl:if test="string-length(patientmedicalenddate) > 0"><high value="{patientmedicalenddate}"/></xsl:if>
					</effectiveTime>
				</xsl:if>
				<!-- B.1.7.1.g - Comments -->
				<xsl:if test="string-length(patientmedicalcomment) > 0">
					<outboundRelationship2 typeCode="COMP">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$Comment}" codeSystem="{$oidObservationCode}"/>
							<value xsi:type="ED"><xsl:value-of select="patientmedicalcomment"/></value>
						</observation>
					</outboundRelationship2>
				</xsl:if>
				<!-- B.1.7.1.r.f - Continuing -->
				<xsl:if test="patientmedicalcontinue = 1 or patientmedicalcontinue = 2 or patientmedicalcontinue = 3">
					<inboundRelationship typeCode="REFR">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$Continuing}" codeSystem="{$oidObservationCode}"/>
							<xsl:choose>
								<xsl:when test="patientmedicalcontinue = 1"><value xsi:type="BL" value="true"/></xsl:when>
								<xsl:when test="patientmedicalcontinue = 2"><value xsi:type="BL" value="false"/></xsl:when>
								<xsl:when test="patientmedicalcontinue = 3"><value xsi:type="BL" nullFlavor="NASK" /></xsl:when>
							</xsl:choose>
						</observation>
					</inboundRelationship>
				</xsl:if>
			</observation>
		</component>
	</xsl:template>
	
	<!-- Patient (past drug therapy) : 
	E2B(R2): element "patientpastdrugtherapy"
	E2B(R3): element "primaryRole"
	-->
	<xsl:template match="patientpastdrugtherapy">
		<component typeCode="COMP">
			<substanceAdministration moodCode="EVN" classCode="SBADM">
				<!-- B.1.8.r.ce Start and End Date -->
				<xsl:if test="string-length(patientdrugstartdate) > 0 or string-length(patientdrugenddate) > 0">
					<effectiveTime xsi:type="IVL_TS">
						<xsl:if test="string-length(patientdrugstartdate) > 0">
							<low value="{patientdrugstartdate}"/>
						</xsl:if>
						<xsl:if test="string-length(patientdrugenddate) > 0">
							<high value="{patientdrugenddate}"/>
						</xsl:if>
					</effectiveTime>
				</xsl:if>
				<!-- B.1.8.r.a Name of Drug as Reported -->
				<xsl:if test="string-length(patientdrugname) > 0">
					<consumable typeCode="CSM">
						<instanceOfKind classCode="INST">
							<kindOfProduct classCode="MMAT" determinerCode="KIND">
								<name><xsl:value-of select="patientdrugname"/></name>
							</kindOfProduct>
						</instanceOfKind>
					</consumable>
				</xsl:if>
				<!-- B.1.8.r.f - Indication -->
				<xsl:if test="string-length(patientdrugindication) > 0">
					<xsl:variable name="isIndicationMeddraCode">
						<xsl:call-template name="isMeddraCode">
							<xsl:with-param name="code" select="patientdrugindication"/>
						</xsl:call-template>
					</xsl:variable>
					<outboundRelationship2 typeCode="RSON">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$Indication}" codeSystem="{$oidObservationCode}"/>
							<xsl:choose>
								<xsl:when test="$isIndicationMeddraCode = 'yes'">
									<value xsi:type="CE" code="{patientdrugindication}" codeSystemVersion="{patientindicationmeddraversion}" codeSystem="{$oidMedDRA}"/>
								</xsl:when>
								<xsl:otherwise>
									<value xsi:type="CE">
										<originalText>
											<xsl:value-of select="patientdrugindication"/>
											<xsl:if test="string-length(patientindicationmeddraversion) > 0"> (<xsl:value-of select="patientindicationmeddraversion"/>)</xsl:if>
										</originalText>
									</value>
								</xsl:otherwise>
							</xsl:choose>
						</observation>
					</outboundRelationship2>
				</xsl:if>
				<!-- B.1.8.r.f - Reaction -->
				<xsl:if test="string-length(patientdrugreaction) > 0">
					<xsl:variable name="isReactionMeddraCode">
						<xsl:call-template name="isMeddraCode">
							<xsl:with-param name="code" select="patientdrugreaction"/>
						</xsl:call-template>
					</xsl:variable>
					<outboundRelationship2 typeCode="CAUS">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$Reaction}" codeSystem="{$oidObservationCode}"/>
							<xsl:choose>
								<xsl:when test="$isReactionMeddraCode = 'yes'">
									<value xsi:type="CE" code="{patientdrugreaction}" codeSystemVersion="{patientdrgreactionmeddraversion}" codeSystem="{$oidMedDRA}"/>
								</xsl:when>
								<xsl:otherwise>
									<value xsi:type="CE">
										<originalText>
											<xsl:value-of select="patientdrugreaction"/>
											<xsl:if test="string-length(patientdrgreactionmeddraversion) > 0"> (<xsl:value-of select="patientdrgreactionmeddraversion"/>)</xsl:if>
										</originalText>
									</value>
								</xsl:otherwise>
							</xsl:choose>
						</observation>
					</outboundRelationship2>
				</xsl:if>
			</substanceAdministration>
		</component>
	</xsl:template>

	<!-- Patient (reported cause of death) : 
	E2B(R2): element "patientdeathreport"
	E2B(R3): element "primaryRole"
	-->
	<xsl:template match="patientdeathcause">
		<subjectOf2 typeCode="SBJ">
			<!-- B.1.9.2 Reported Cause of Death -->
			<observation moodCode="EVN" classCode="OBS">
				<code code="{$ReportedCauseOfDeath}" codeSystem="{$oidObservationCode}"/>
				<xsl:variable name="isMeddraCode">
					<xsl:call-template name="isMeddraCode">
						<xsl:with-param name="code" select="patientdeathreport"/>
					</xsl:call-template>
				</xsl:variable>
				<xsl:choose>
					<xsl:when test="$isMeddraCode = 'yes'">
						<value xsi:type="CE" code="{patientdeathreport}" codeSystemVersion="{patientdeathreportmeddraversion}" codeSystem="{$oidMedDRA}"/>
					</xsl:when>
					<xsl:otherwise>
						<value xsi:type="CE">
							<originalText>
								<xsl:value-of select="patientdeathreport"/>
								<xsl:if test="string-length(patientdeathreportmeddraversion) > 0"> (<xsl:value-of select="patientdeathreportmeddraversion"/>)</xsl:if>
							</originalText>
						</value>
					</xsl:otherwise>
				</xsl:choose>
			</observation>
		</subjectOf2>
	</xsl:template>
	
	<!-- Patient (death) : 
	E2B(R2): element "patientdeath"
	E2B(R3): element "primaryRole"
	-->
	<xsl:template match="patientdeath">
		<!-- B.1.9.2 - Patient Death Cause -->
		<xsl:apply-templates select="patientdeathcause"/>
		<!-- B.1.9.3-4 Autopsy -->
		<xsl:if test="string-length(patientautopsyyesno) > 0">
			<subjectOf2 typeCode="SBJ">
				<!-- B.1.9.3 Autopsy Done Yes/No -->
				<observation moodCode="EVN" classCode="OBS">
					<code code="{$Autopsy}" codeSystem="{$oidObservationCode}"/>
					<xsl:choose>
						<xsl:when test="patientautopsyyesno = 1">
							<value xsi:type="BL" value="true"/>
						</xsl:when>
						<xsl:when test="patientautopsyyesno = 2">
							<value xsi:type="BL" value="false"/>
						</xsl:when>
						<xsl:when test="patientautopsyyesno = 3">
							<value xsi:type="BL" nullFlavor="UNK"/>
						</xsl:when>
					</xsl:choose>
					<xsl:apply-templates select="patientautopsy"/>
				</observation>
			</subjectOf2>
		</xsl:if>
	</xsl:template>
	
	<!-- Patient (autopsy-determined cause of death) : 
	E2B(R2): element "patientautopsy"
	E2B(R3): element "primaryRole"
	-->
	<xsl:template match="patientautopsy">
		<!-- B.1.9.4 Autopsy-determined Cause of Death -->
		<outboundRelationship2 typeCode="DRIV">
			<observation moodCode="EVN" classCode="OBS">
				<code code="{$CauseOfDeath}" codeSystem="{$oidObservationCode}"/>
				<xsl:variable name="isMeddraCode">
					<xsl:call-template name="isMeddraCode">
						<xsl:with-param name="code" select="patientdetermineautopsy"/>
					</xsl:call-template>
				</xsl:variable>
				<xsl:choose>
					<xsl:when test="$isMeddraCode = 'yes'">
						<value xsi:type="CE" code="{patientdetermineautopsy}" codeSystemVersion="{patientdetermautopsmeddraversion}" codeSystem="{$oidMedDRA}"/>
					</xsl:when>
					<xsl:otherwise>
						<value xsi:type="CE">
							<originalText>
								<xsl:value-of select="patientdetermineautopsy"/>
								<xsl:if test="string-length(patientdetermautopsmeddraversion) > 0"> (<xsl:value-of select="patientdetermautopsmeddraversion"/>)</xsl:if>
							</originalText>
						</value>
					</xsl:otherwise>
				</xsl:choose>
			</observation>
		</outboundRelationship2>
	</xsl:template>
	
</xsl:stylesheet>
