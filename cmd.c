/**
 * Operating Systems 2013-2017 - Assignment 2
 *
 * TODO Name, Group
 *
 */

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>

#include <fcntl.h>
#include <unistd.h>

#include "cmd.h"
#include "utils.h"

#define READ		0
#define WRITE		1

#include <stdio.h>
#include <string.h>
#include <stdlib.h>



/**
 * Internal change-directory command.
 */
static bool shell_cd(word_t *dir)//TODO
{
	/* TODO execute cd */
	int ret = chdir(dir->string);
	//DIE(ret < 0, "");
	if(ret < 0)
        perror("bash: cd");
	return ret;
}

/**
 * Internal exit/quit command.
 */
static int shell_exit(void)
{
	/* TODO execute exit/quit */

	exit(0);
	return 0; /* TODO replace with actual exit code */
}

/**
 * Parse a simple command (internal, environment variable assignment,
 * external command).
 */
static int parse_simple(simple_command_t *s, int level, command_t *father)
{
	/* TODO sanity checks */
	//eroare -> return -1
	//current directory -> cd dir > fisier


	/* TODO if builtin command, execute the command */
	if(strcmp(s->verb->string, "cd") == 0)
	{
		if(s->out){//output redirect(<)
			int fd = open(s->out->string, O_WRONLY | O_CREAT | O_TRUNC, 0644);
			close(fd);
		}

		if(s->params){
			return shell_cd(s->params);
		}
		else{
			word_t *t = malloc(sizeof(word_t));
			t->string = getenv("HOME");
			int ret = shell_cd(t);
			return ret;
		}
	}
	if(strcmp(s->verb->string, "exit") == 0 || strcmp(s->verb->string, "quit") == 0)
		return shell_exit();


	/* TODO if variable assignment, execute the assignment and return
	 * the exit status
	 */
	if(s->verb->next_part != NULL && strcmp(s->verb->next_part->string, "=") == 0){
		//printf("Variable assignment %s %s\n", s->verb->string, s->verb->next_part->next_part->string);
		word_t *argument = s->verb->next_part->next_part;
		//printf("%s\n", argument->string);
		char *valoare = malloc(0);

		while(argument != NULL){
			if(argument->expand){
				if(getenv(argument->string) != NULL){
					valoare = realloc(valoare, (strlen(valoare) + strlen(getenv(argument->string))) * sizeof(char));
					strcat(valoare, getenv(argument->string));
				}
			}
			else{
				valoare = realloc(valoare, (strlen(valoare) + strlen(argument->string)) * sizeof(char));
				strcat(valoare, argument->string);
			}
			argument = argument->next_part;
		}


		int ret = setenv(s->verb->string, valoare, 1);
		if (ret == -1){
			perror("");
			return -1;
		}
		return 0;
		//printf("%s\n", getenv(s->verb->string));
	}


	/* TODO if external command:
	 *   1. fork new process
	 *     2c. perform redirections in child
	 *     3c. load executable in child
	 *   2. wait for child
	 *   3. return exit status
	 */

	pid_t pid;
  	int status;

  	if ((pid = fork()) == -1) {
        perror("fork error");
        exit(0);//TODO -> exit code
    }
  	else if(pid == 0){
		
		if(s->in){//input redirect(<)
			word_t *part = s->in;
			char *param = malloc(100*sizeof(char)); param[0] = '\0';
			while(part){
				//printf("%s\n", part->string);

				if(part->expand) {//getenv
					if(getenv(part->string) != NULL)
						strcat(param, getenv(part->string));
					else
						strcat(param, "");
				}
				else
					strcat(param, part->string);

				part = part->next_part;
			}


			int fd = open(param, O_RDONLY, 0644);
			dup2(fd, STDIN_FILENO);
			close(fd);
		}

		if(s->out){//output redirect>
			int fd;
			word_t *part = s->out;
			char *param = malloc(100*sizeof(char)); param[0] = '\0';
			while(part){
				//printf("%s\n", part->string);

				if(part->expand) {//getenv
					if(getenv(part->string) != NULL)
						strcat(param, getenv(part->string));
					else
						strcat(param, "");
				}
				else
					strcat(param, part->string);

				part = part->next_part;
			}

			if(s->err && strcmp(s->out->string, s->err->string) == 0){//out+err redirect(&>)
				fd = open(param, O_WRONLY | O_CREAT | O_TRUNC, 0644);
				dup2(fd, STDOUT_FILENO);
				dup2(fd, STDERR_FILENO);//merge asa?
			}
			else if (!s->err || (s->err && strcmp(s->out->string, s->err->string) != 0)){//only output redirect
				if(s->io_flags == 1){//append(>>)
					fd = open(param, O_WRONLY | O_CREAT | O_APPEND, 0644);
					dup2(fd, STDOUT_FILENO);
				}
				else{//normal(>)
					fd = open(param, O_WRONLY | O_CREAT | O_TRUNC, 0644);
					dup2(fd, STDOUT_FILENO);
				}
			}
			close(fd);
		}

		if(s->err){//error redirect
			word_t *part = s->err;
			char *param = malloc(100*sizeof(char)); param[0] = '\0';
			while(part){
				//printf("%s\n", part->string);

				if(part->expand) {//getenv
					if(getenv(part->string) != NULL)
						strcat(param, getenv(part->string));
					else
						strcat(param, "");
				}
				else
					strcat(param, part->string);

				part = part->next_part;
			}

			if((s->out && strcmp(s->out->string, s->err->string) != 0) || (!s->out)){//TODO: ok ????????????????????
				int fd;
				if(s->io_flags == 2){//append(2>>)
					fd = open(param, O_WRONLY | O_CREAT | O_APPEND, 0644);
					dup2(fd, STDERR_FILENO);
				}
				else{//normal(2>)
					fd = open(param, O_WRONLY | O_CREAT | O_TRUNC, 0644);
					dup2(fd, STDERR_FILENO);
				}
				close(fd);
			}
		}

		//***************************

  		int nr_params = 0;
  		char **argv = malloc((2+nr_params) * sizeof(char*));
  		argv[0] = malloc(20*sizeof(char));
  		strcpy(argv[0], s->verb->string);
  		word_t *params = s->params;
		while(params){
			nr_params++;
			argv = realloc(argv, (2+nr_params) * sizeof(char*));
			argv[nr_params] = malloc(10*sizeof(char));


			//TODO: make function
			word_t *part = params;
			char *param = malloc(100*sizeof(char)); param[0] = '\0';
			while(part){
				//printf("%s\n", part->string);

				if(part->expand) {//getenv
					if(getenv(part->string) != NULL)
						strcat(param, getenv(part->string));
					else
						strcat(param, "");
				}
				else
					strcat(param, part->string);

				part = part->next_part;
			}
			strcpy(argv[nr_params], param);
			


			params = params->next_word;
		}
		argv[1+nr_params] = NULL;


		if(execvp(s->verb->string, argv) == -1){
			fprintf(stderr, "Execution failed for '%s'\n", s->verb->string);
			exit(-1);
		}
		else
			exit(0);
		//return ???
  	}
  	else{
  		//printf("Parent process\n");
  		int wait_ret = waitpid(pid, &status, 0);
		DIE(wait_ret < 0, "waitpid");
		//printf("parse simple: %d\n", WEXITSTATUS(status));
		return WEXITSTATUS(status);
  	}



	//return ret; /* TODO replace with actual exit status */
}

/**
 * Process two commands in parallel, by creating two children.
 */
int do_in_parallel(command_t *cmd1, command_t *cmd2, int level,
		command_t *father)
{
	/* TODO execute cmd1 and cmd2 simultaneously */
	//printf("%s %s\n", cmd1->scmd->verb->string, cmd2->scmd->verb->string);

	//parse_command(cmd1) + parse_command(cmd2) -> 2 forks / 1 fork
	pid_t pid1, pid2;
  	int status1, status2;

  	if ((pid1 = fork()) == -1) {
        perror("fork error");
        exit(0);//TODO -> exit code
    }
  	else if(pid1 == 0){
  		//child process
		if(parse_command(cmd1, level, father) == -1){//level + 1???
			//perror();
			fprintf(stderr, "Execution failed for '%s'\n", cmd1->scmd->verb->string);
			exit(-1);
		}
		else
			exit(0);
  	}
  	else{
  		//parent process
  		//break;
  	}


  	if ((pid2 = fork()) == -1) {
        perror("fork error");
        exit(0);//TODO -> exit code
    }
  	else if(pid2 == 0){
  		//child process
		if(parse_command(cmd2, level, father) == -1){//level + 1???
			//perror();
			fprintf(stderr, "Execution failed for '%s'\n", cmd2->scmd->verb->string);
			exit(-1);
		}
		else
			exit(0);
  	}
  	else{
  		//parent process
  		//break;
  	}

  	//ok ???
  	int wait_ret1 = waitpid(pid1, &status1, 0);
	DIE(wait_ret1 < 0, "waitpid1");
	int wait_ret2 = waitpid(pid2, &status2, 0);
	DIE(wait_ret2 < 0, "waitpid2");

	return WEXITSTATUS(status1);

	/* TODO replace with actual exit status */
}

/**
 * Run commands by creating an anonymous pipe (cmd1 | cmd2)
 */
int do_on_pipe(command_t *cmd1, command_t *cmd2, int level,
		command_t *father)
{
	/* TODO redirect the output of cmd1 to the input of cmd2 */


	//execute cmd1 -> redirect STDOUT -> file
	//execute cmd2 -> redirect file -> STDIN
	//remove file

	pid_t pid1, pid2;
  	int status1, status2;

  	/*printf("1: %s\n", cmd1->cmd1->scmd->verb->string);
  	printf("1: %s\n", cmd1->cmd2->scmd->verb->string);
  	printf("2: %s\n", cmd2->scmd->verb->string);*/

	char name[] = "/tmp/fileXXXXXX";
	int fd = mkstemp(name);

		if ((pid1 = fork()) == -1) {
        perror("fork error");
        exit(0);//TODO -> exit code
    }
  	else if(pid1 == 0){
  		//child process
  		//int fd = open(name, O_WRONLY | O_CREAT | O_TRUNC, 0644);
		dup2(fd, STDOUT_FILENO);
		close(fd);

		if(parse_command(cmd1, level, father) == -1){
			fprintf(stderr, "Execution failed for '%s'\n", cmd1->scmd->verb->string);
			exit(-1);
		}
		else
			exit(0);
  	}
  	else{
  		//parent process
  		int wait_ret1 = waitpid(pid1, &status1, 0);
		DIE(wait_ret1 < 0, "waitpid1");	
  	}

  	//cmd2
  	if ((pid2 = fork()) == -1) {
        perror("fork error");
        exit(0);//TODO -> exit code
    }
  	else if(pid2 == 0){
  		//child process
  		int fd = open(name, O_RDONLY, 0644);
		dup2(fd, STDIN_FILENO);
		close(fd);

		int ret = parse_command(cmd2, level, father); //TODO: parse_command return value -> parse simple return value
		//printf("%d\n", ret);
		if(ret == -1){//level + 1???
			//perror();
			fprintf(stderr, "Execution failed for '%s'\n", cmd2->scmd->verb->string);
			exit(-1);
		}
		else
			exit(ret);
  	}
  	else{
  		//parent process
  		int wait_ret2 = waitpid(pid2, &status2, 0);
		remove(name);
		DIE(wait_ret2 < 0, "waitpid2");

		//printf("%d\n", WEXITSTATUS(status2));
		return WEXITSTATUS(status2);
  	}

	 /* TODO replace with actual exit status */
}

/**
 * Parse and execute a command.
 */
int parse_command(command_t *c, int level, command_t *father)
{
	/* TODO sanity checks */

	if (c->op == OP_NONE) {
		/* TODO execute a simple command */
		//printf("simple %d\n", level);
		return parse_simple(c->scmd, level, father);

		 /* TODO replace with actual exit code of command */
	}

	int r;
	switch (c->op) {
	case OP_SEQUENTIAL:
		/* TODO execute the commands one after the other */
		//printf(";\n");
		parse_command(c->cmd1, level + 1, c);
		parse_command(c->cmd2, level + 1, c);
		break;

	case OP_PARALLEL:
		/* TODO execute the commands simultaneously */
		//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		//printf("&\n");
		return do_in_parallel(c->cmd1, c->cmd2, level + 1, c);
		break;

	case OP_CONDITIONAL_NZERO:
		/* TODO execute the second command only if the first one
		 * returns non zero
		 */
		//printf("||\n");
		r = parse_command(c->cmd1, level + 1, c);
		if (r != 0)
			return parse_command(c->cmd2, level + 1, c);
		break;

	case OP_CONDITIONAL_ZERO:
		/* TODO execute the second command only if the first one
		 * returns zero
		 */
		//printf("&&\n");
		r = parse_command(c->cmd1, level + 1, c);
		if (r == 0)
			return parse_command(c->cmd2, level + 1, c);
		break;

	case OP_PIPE:
		/* TODO redirect the output of the first command to the
		 * input of the second
		 */
		//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		//printf("|\n");
		r = do_on_pipe(c->cmd1, c->cmd2, level + 1, c);
		//printf("Pipe: %d\n", r);
		return r;
		break;

	default:
		return SHELL_EXIT;
	}

	return 0; /* TODO replace with actual exit code of command */
}
