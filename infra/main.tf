/*===============================
#            S3
===============================*/

resource "aws_instance" "app_server" {
  ami           = "ami-056914720476ddd8c"
  instance_type = "t2.micro"

}
