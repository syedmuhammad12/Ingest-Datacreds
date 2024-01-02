<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade - A.5 Part)

			Version:		0.9
		Date:			21/06/2011
		Status:		Step 4
		Author:		Laurent DESQUEPER (EU)

		Version:		1.1
		Date:			07/10/2016
		Status:			Draft
		Author:			Nick Halsey (EU)
	Addition of ICH CodeSystemVersion and EU specific data fields
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif">

	<!-- Study : 
	E2B(R2): element "primarysource"
	E2B(R3): element "primaryRole"
	-->
	<xsl:template match="primarysource" mode="study">
		<xsl:if test ="position()=1">
			<xsl:if test="string-length(studyname) > 0">
				<xsl:choose>
					<xsl:when test="substring(studyname,15,1) ='#'">
					<subjectOf1 typeCode="SBJ">
							<researchStudy classCode="CLNTRL" moodCode="EVN">
								<!-- A.5.3 Sponsor Study Number -->
								<xsl:if test="string-length(sponsorstudynumb) > 0">
									<id extension="{sponsorstudynumb}" root="{$SponsorStudyNumber}"/>
								</xsl:if>
								<!-- A.5.4 Study Type in which the Reaction(s)/Event(s) were Observed -->
								<xsl:if test="string-length(observestudytype) > 0">
									<code code="{observestudytype}" codeSystem="{$oidStudyType}" codeSystemVersion="{$oidStudyTypeCSV}"/>
								</xsl:if>
								<!-- A.5.2 Study Name -->
									<title><xsl:value-of select="substring(studyname,16,string-length(studyname))"/></title>
								<authorization typeCode="AUTH">
									<studyRegistration classCode="ACT" moodCode="EVN">
										<id extension="{substring(studyname,0,15)}" root="{$StudyRegistrationNumber}"/>
										<!-- C.5.1.r.1: Study Registration Number #1 -->
										<author typeCode="AUT">
											<territorialAuthority classCode="TERR">
												<governingPlace classCode="COUNTRY" determinerCode="INSTANCE">
													<code code="EU" codeSystem="1.0.3166.1.2.2"/>
													<!-- C.5.1.r.2: Study Registration Country #1 -->
												</governingPlace>
											</territorialAuthority>
										</author>
									</studyRegistration>
								</authorization>
							</researchStudy>
						</subjectOf1>
					</xsl:when>			
					<xsl:otherwise>
						<subjectOf1 typeCode="SBJ">
							<researchStudy classCode="CLNTRL" moodCode="EVN">
								<!-- A.5.3 Sponsor Study Number -->
								<xsl:if test="string-length(sponsorstudynumb) > 0">
									<id extension="{sponsorstudynumb}" root="{$SponsorStudyNumber}"/>
								</xsl:if>
								<!-- A.5.4 Study Type in which the Reaction(s)/Event(s) were Observed -->
								<xsl:if test="string-length(observestudytype) > 0">
									<code code="{observestudytype}" codeSystem="{$oidStudyType}" codeSystemVersion="{$oidStudyTypeCSV}"/>
								</xsl:if>
								<!-- A.5.2 Study Name -->
								<xsl:if test="string-length(studyname) > 0">
									<title><xsl:value-of select="studyname"/></title>
								</xsl:if>
							</researchStudy>
						</subjectOf1>
					</xsl:otherwise>
				</xsl:choose>		
			</xsl:if>
		</xsl:if>
	</xsl:template>
	
</xsl:stylesheet>
